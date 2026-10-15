import base64
import gc
import io
import time
import uuid
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from PIL import Image
import numpy as np

from backend.config import INPUT_DIR, OUTPUT_DIR
from backend.services.background_analyzer import analyze_background
from backend.services.chroma_key import segment_chroma_key
from backend.services.background_removal import get_background_remover
from backend.services.birefnet_portrait import get_birefnet_remover
from backend.services.mediapipe_segmentation import get_mediapipe_segmentor
from backend.services.mask_refinement import refine_hybrid_mask, evaluate_mask_quality
from backend.services.image_compositor import composite_studio_background
from backend.utils.image_ops import validate_image_file, load_and_preprocess_image, resize_if_needed

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/photo", tags=["photo"])

# In-memory session cache for instant zero-AI compositing and on-demand full-res export
# Key: session_id -> metadata and file paths
SESSION_CACHE: Dict[str, Dict[str, Any]] = {}

MAX_PREVIEW_DIM = 1200  # Lightweight preview size for snappy UI operations without lag


def to_base64_data_url(img: Image.Image, max_dim: int = MAX_PREVIEW_DIM) -> str:
    """Creates a lightweight web preview Data URL."""
    w, h = img.size
    if max(w, h) > max_dim:
        scale = max_dim / float(max(w, h))
        thumb = img.resize((int(w * scale), int(h * scale)), Image.Resampling.BILINEAR)
    else:
        thumb = img.copy()

    buf = io.BytesIO()
    if thumb.mode in ("RGBA", "LA", "L"):
        thumb.save(buf, format="PNG")
        mime = "image/png"
    else:
        thumb.save(buf, format="JPEG", quality=88)
        mime = "image/jpeg"

    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    del thumb
    return f"data:{mime};base64,{encoded}"


@router.post("/process-background")
async def process_background(
    file: UploadFile = File(...),
    method_mode: str = Form("auto"),  # "auto", "birefnet", "u2netp", "chroma_key"
    smoothness: float = Form(1.0)
):
    """
    STAGE A: EXPENSIVE AI PROCESSING (Runs ONCE per photo)
    3-Tier routing:
      Tier 1 — Chroma Key:  ~instant, for green/blue uniform backdrops (auto or manual)
      Tier 2 — MediaPipe:   ~1-5s CPU, default for all portraits/complex scenes
      Tier 3 — BiRefNet:    ~60-180s CPU, optional 'Studio Quality' on manual override
    """
    total_start = time.time()
    file_bytes = await file.read()
    file_size = len(file_bytes)

    # 1. Validation & Preprocessing
    t_pre_start = time.time()
    try:
        validate_image_file(file.filename, file_size)
        original_img, original_size = load_and_preprocess_image(file_bytes)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Image validation error: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")

    session_id = str(uuid.uuid4())[:8]
    sanitized_filename = f"{session_id}_original{Path(file.filename).suffix.lower()}"
    input_filepath = INPUT_DIR / sanitized_filename
    with open(input_filepath, "wb") as f:
        f.write(file_bytes)

    # Downscale for segmentation: 1024px max for MediaPipe/BiRefNet (faster, sufficient quality)
    img_for_seg, was_resized = resize_if_needed(original_img, max_dim=1024)
    seg_size = img_for_seg.size
    t_pre_ms = int((time.time() - t_pre_start) * 1000)

    # 2. Background Analysis
    t_analysis_start = time.time()
    rgb_seg_np = np.array(img_for_seg)
    bg_analysis = analyze_background(rgb_seg_np)
    t_analysis_ms = int((time.time() - t_analysis_start) * 1000)

    # --- 3-Tier Method Selection ---
    # method_mode values: "auto", "mediapipe", "birefnet", "u2netp", "chroma_key"
    if method_mode == "birefnet":
        selected_method = "birefnet"
        method_reason = "Manual override: BiRefNet-Portrait (Studio Quality — slow on CPU)"
    elif method_mode == "u2netp":
        selected_method = "u2netp"
        method_reason = "Manual override: U2NetP (Legacy lightweight AI)"
    elif method_mode == "chroma_key":
        selected_method = "chroma_key"
        method_reason = "Manual override: Chroma Key"
    elif method_mode == "mediapipe":
        selected_method = "mediapipe"
        method_reason = "Manual override: MediaPipe Selfie Segmentation (Fast CPU)"
    else:  # auto
        if bg_analysis["is_uniform"] and bg_analysis["detected_color"] in ("green", "blue"):
            # Tier 1: Uniform color backdrop -> instant chroma key
            selected_method = "chroma_key"
            method_reason = f"Uniform {bg_analysis['detected_color']} backdrop (Score: {bg_analysis['uniformity_score']:.2f}) -> Auto Chroma Key"
        else:
            # Tier 2: All other scenes -> MediaPipe (fast, good quality)
            selected_method = "mediapipe"
            method_reason = f"Portrait/complex scene (Score: {bg_analysis['uniformity_score']:.2f}) -> MediaPipe Fast AI"

    # 3. Model Inference
    t_seg_start = time.time()
    try:
        if selected_method == "chroma_key":
            raw_mask_small, despilled_small = segment_chroma_key(
                rgb_img=rgb_seg_np,
                target_color_rgb=bg_analysis["estimated_color_rgb"],
                tolerance=0.28,
                softness=0.12,
                protect_skin=True
            )
            working_small_np = despilled_small
        elif selected_method == "mediapipe":
            mp_seg = get_mediapipe_segmentor()
            raw_mask_small, _ = mp_seg.segment_mask(img_for_seg, seg_resolution=1024)
            working_small_np = rgb_seg_np
        elif selected_method == "birefnet":
            remover = get_birefnet_remover()
            raw_mask_small, _ = remover.segment_mask(img_for_seg)
            working_small_np = rgb_seg_np
        else:  # u2netp
            remover = get_background_remover()
            raw_mask_small, _ = remover.segment_mask(img_for_seg)
            working_small_np = rgb_seg_np
    except Exception as e:
        logger.error(f"Segmentation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Segmentation failed: {str(e)}")

    t_seg_ms = int((time.time() - t_seg_start) * 1000)

    # 4. Mask Refinement
    t_refine_start = time.time()
    refined_small_mask = refine_hybrid_mask(
        raw_mask=raw_mask_small,
        guide_img=working_small_np,
        smoothness=smoothness
    )
    t_refine_ms = int((time.time() - t_refine_start) * 1000)

    del rgb_seg_np, working_small_np
    gc.collect()

    # 5. Quality Assessment
    quality_eval = evaluate_mask_quality(refined_small_mask)

    # 6. Save Full Resolution Alpha Mask to Disk
    refined_small_pil = Image.fromarray(refined_small_mask, mode="L")
    if was_resized:
        refined_full_mask = refined_small_pil.resize(original_size, Image.Resampling.LANCZOS)
    else:
        refined_full_mask = refined_small_pil

    mask_filename = f"{session_id}_full_mask.png"
    mask_filepath = OUTPUT_DIR / mask_filename
    refined_full_mask.save(mask_filepath, format="PNG")

    # 7. Generate Dedicated Lightweight Preview RGBA
    # Resize original image to preview size
    preview_img, _ = resize_if_needed(original_img, max_dim=MAX_PREVIEW_DIM)
    preview_mask = refined_small_pil.resize(preview_img.size, Image.Resampling.BILINEAR)

    preview_rgba = preview_img.convert("RGBA")
    preview_rgba.putalpha(preview_mask)

    # Save transparent preview data URL
    transparent_preview_data_url = to_base64_data_url(preview_rgba)
    original_preview_data_url = to_base64_data_url(preview_img)
    mask_preview_data_url = to_base64_data_url(preview_mask)

    # 8. Store Session in Memory Cache for Instant Full-Resolution Export
    SESSION_CACHE[session_id] = {
        "original_path": input_filepath,
        "mask_path": mask_filepath,
        "filename": file.filename,
        "original_size": original_size,
        "preview_size": preview_img.size,
        "method": selected_method,
        "timestamp": time.time()
    }

    # Free heavy memory
    del original_img, preview_rgba, refined_full_mask
    gc.collect()

    total_time_ms = int((time.time() - total_start) * 1000)

    friendly_name = {
        "mediapipe": "MediaPipe Selfie (Fast CPU)",
        "birefnet":  "BiRefNet-Portrait (Studio Quality)",
        "u2netp":    "U2NetP (Legacy Lightweight)",
        "chroma_key": "Chroma Key (Instant)"
    }.get(selected_method, selected_method)

    return JSONResponse(
        content={
            "success": True,
            "session_id": session_id,
            "filename": file.filename,
            "original_dimensions": {"width": original_size[0], "height": original_size[1]},
            "preview_dimensions": {"width": preview_img.size[0], "height": preview_img.size[1]},
            "method_info": {
                "selected_method": friendly_name,
                "method_key": selected_method,
                "reason": method_reason,
                "analysis": bg_analysis
            },
            "quality": quality_eval,
            "timings": {
                "preprocessing_ms": t_pre_ms,
                "analysis_ms": t_analysis_ms,
                "segmentation_ms": t_seg_ms,
                "mask_refinement_ms": t_refine_ms,
                "total_ms": total_time_ms,
            },
            "previews": {
                "original": original_preview_data_url,
                "transparent_preview": transparent_preview_data_url,
                "mask_preview": mask_preview_data_url
            }
        }
    )


@router.post("/export-final")
async def export_final(
    session_id: str = Form(...),
    bg_type: str = Form("transparent"),
    custom_color: Optional[str] = Form(None)
):
    """
    FULL-RESOLUTION EXPORT (Triggered ONLY when user clicks 'Download Image')
    Composites stored 100% full-resolution original image + full-resolution mask.
    Zero AI re-run. Fast alpha blending at native camera resolution.
    """
    t0 = time.time()
    session = SESSION_CACHE.get(session_id)
    if not session or not Path(session["original_path"]).exists():
        # Fallback check on disk
        mask_path = OUTPUT_DIR / f"{session_id}_full_mask.png"
        orig_matches = list(INPUT_DIR.glob(f"{session_id}_original.*"))
        if mask_path.exists() and orig_matches:
            session = {
                "original_path": orig_matches[0],
                "mask_path": mask_path,
                "filename": f"photo_{session_id}.jpg"
            }
        else:
            raise HTTPException(status_code=404, detail="Session expired or not found. Please re-upload.")

    try:
        # Load native full-resolution original with EXIF orientation correction
        from PIL import ImageOps
        orig_img = Image.open(session["original_path"])
        orig_img = ImageOps.exif_transpose(orig_img)
        orig_img = orig_img.convert("RGBA")
        full_mask = Image.open(session["mask_path"]).convert("L")

        orig_img.putalpha(full_mask)

        # Composite background
        final_img = composite_studio_background(orig_img, bg_type=bg_type, custom_hex=custom_color)

        output_filename = f"{session_id}_export_{bg_type}.png"
        output_filepath = OUTPUT_DIR / output_filename
        final_img.save(output_filepath, format="PNG", optimize=True)

        export_time_ms = int((time.time() - t0) * 1000)
        logger.info(f"Full-res export for {session_id} generated in {export_time_ms} ms ({final_img.size[0]}x{final_img.size[1]})")

        del orig_img, full_mask, final_img
        gc.collect()

        return JSONResponse(
            content={
                "success": True,
                "session_id": session_id,
                "export_time_ms": export_time_ms,
                "download_url": f"/api/photo/download/{output_filename}"
            }
        )
    except Exception as e:
        logger.error(f"Full-res export failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-models")
async def compare_models(
    file: UploadFile = File(...),
    bg_type: str = Form("white")
):
    """
    Advanced Model Comparison Mode (Memory-Safe):
    Executes BiRefNet-Portrait, U2NetP, and Chroma Key on the downscaled representation,
    avoiding memory exhaustion on 20MP+ photos while generating side-by-side previews.
    """
    file_bytes = await file.read()
    validate_image_file(file.filename, len(file_bytes))
    original_img, original_size = load_and_preprocess_image(file_bytes)

    # Use max 1200 for fast comparison without RAM bloat
    img_for_comp, was_resized = resize_if_needed(original_img, max_dim=MAX_PREVIEW_DIM)
    rgb_comp_np = np.array(img_for_comp)

    comparison_results = {}

    # 0. MediaPipe Selfie Segmenter (Fastest AI)
    try:
        t0 = time.time()
        mp_segmentor = get_mediapipe_segmentor()
        m_raw_mask, _ = mp_segmentor.segment_mask(img_for_comp, seg_resolution=1024)
        m_ref_mask = refine_hybrid_mask(m_raw_mask, rgb_comp_np, smoothness=1.0)
        m_trans = img_for_comp.convert("RGBA")
        m_trans.putalpha(Image.fromarray(m_ref_mask, mode="L"))
        m_final = composite_studio_background(m_trans, bg_type=bg_type)
        m_time = int((time.time() - t0) * 1000)

        comparison_results["mediapipe"] = {
            "name": "MediaPipe Selfie (Fast)",
            "time_ms": m_time,
            "inference_res": f"{img_for_comp.size[0]}x{img_for_comp.size[1]}",
            "output_res": f"{original_size[0]}x{original_size[1]}",
            "preview": to_base64_data_url(m_final),
            "status": "Success"
        }
        del m_trans, m_final
        gc.collect()
    except Exception as e:
        comparison_results["mediapipe"] = {"name": "MediaPipe Selfie", "error": str(e)}

    # 1. BiRefNet-Portrait
    try:
        t0 = time.time()
        birefnet_remover = get_birefnet_remover()
        b_raw_mask, _ = birefnet_remover.segment_mask(img_for_comp)
        b_ref_mask = refine_hybrid_mask(b_raw_mask, rgb_comp_np, smoothness=1.0)
        b_trans = img_for_comp.convert("RGBA")
        b_trans.putalpha(Image.fromarray(b_ref_mask, mode="L"))
        b_final = composite_studio_background(b_trans, bg_type=bg_type)
        b_time = int((time.time() - t0) * 1000)

        comparison_results["birefnet"] = {
            "name": "BiRefNet-Portrait",
            "time_ms": b_time,
            "inference_res": "1024x1024",
            "output_res": f"{original_size[0]}x{original_size[1]}",
            "preview": to_base64_data_url(b_final),
            "status": "Success"
        }
        del b_trans, b_final
        gc.collect()
    except Exception as e:
        comparison_results["birefnet"] = {"name": "BiRefNet-Portrait", "error": str(e)}

    # 2. U2NetP
    try:
        t0 = time.time()
        u2netp_remover = get_background_remover()
        u_raw_mask, _ = u2netp_remover.segment_mask(img_for_comp)
        u_ref_mask = refine_hybrid_mask(u_raw_mask, rgb_comp_np, smoothness=1.0)
        u_trans = img_for_comp.convert("RGBA")
        u_trans.putalpha(Image.fromarray(u_ref_mask, mode="L"))
        u_final = composite_studio_background(u_trans, bg_type=bg_type)
        u_time = int((time.time() - t0) * 1000)

        comparison_results["u2netp"] = {
            "name": "U2NetP (Lightweight)",
            "time_ms": u_time,
            "inference_res": "320x320",
            "output_res": f"{original_size[0]}x{original_size[1]}",
            "preview": to_base64_data_url(u_final),
            "status": "Success"
        }
        del u_trans, u_final
        gc.collect()
    except Exception as e:
        comparison_results["u2netp"] = {"name": "U2NetP", "error": str(e)}

    # 3. Chroma Key
    try:
        t0 = time.time()
        bg_analysis = analyze_background(rgb_comp_np)
        c_raw_mask, c_despilled = segment_chroma_key(
            rgb_img=rgb_comp_np,
            target_color_rgb=bg_analysis["estimated_color_rgb"],
            tolerance=0.28,
            softness=0.12,
            protect_skin=True
        )
        c_ref_mask = refine_hybrid_mask(c_raw_mask, c_despilled, smoothness=1.0)
        c_trans = Image.fromarray(c_despilled).convert("RGBA")
        c_trans.putalpha(Image.fromarray(c_ref_mask, mode="L"))
        c_final = composite_studio_background(c_trans, bg_type=bg_type)
        c_time = int((time.time() - t0) * 1000)

        comparison_results["chroma_key"] = {
            "name": "Chroma Key",
            "time_ms": c_time,
            "inference_res": f"Direct ({img_for_comp.size[0]}x{img_for_comp.size[1]})",
            "output_res": f"{original_size[0]}x{original_size[1]}",
            "uniformity_score": bg_analysis["uniformity_score"],
            "detected_color": bg_analysis["detected_color"],
            "preview": to_base64_data_url(c_final),
            "status": "Success"
        }
        del c_trans, c_final, rgb_comp_np
        gc.collect()
    except Exception as e:
        comparison_results["chroma_key"] = {"name": "Chroma Key", "error": str(e)}

    return JSONResponse(
        content={
            "success": True,
            "filename": file.filename,
            "original_dimensions": {"width": original_size[0], "height": original_size[1]},
            "results": comparison_results
        }
    )


@router.get("/download/{filename}")
async def download_file(filename: str):
    """Serves clean output images."""
    safe_name = Path(filename).name
    target_path = OUTPUT_DIR / safe_name
    if not target_path.exists() or not target_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=target_path, filename=safe_name, media_type="image/png")
