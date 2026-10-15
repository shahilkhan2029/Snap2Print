"""
Evaluation and benchmark test suite for Snap2Print Phase 1.
Tests:
- Original vs Raw Mask vs Refined Mask generation
- Background spill suppression and edge preservation
- Multi-background rendering (Transparent, White, Blue, Custom)
- Detailed pipeline timing telemetry (preprocessing, inference, refinement, compositing)
- Quality score heuristic validation
- Comparison export directory generation for studio visual inspection
"""
import sys
import time
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.services.background_removal import get_background_remover
from backend.services.mask_refinement import (
    refine_mask_edges,
    suppress_color_spill,
    evaluate_mask_quality
)
from backend.services.image_processing import apply_alpha_to_image, composite_on_background


def create_realistic_evaluation_portrait(filepath: Path) -> Image.Image:
    """Creates a portrait with challenging hair fringes and studio background."""
    img = Image.new("RGB", (800, 1000), color=(50, 160, 90)) # Green-tinted studio backdrop
    draw = ImageDraw.Draw(img)

    # Torso with clothing
    draw.polygon([(200, 1000), (320, 620), (480, 620), (600, 1000)], fill=(30, 45, 80)) # Dark suit
    # Shirt collar & neck
    draw.polygon([(360, 620), (400, 720), (440, 620)], fill=(245, 245, 250)) # White shirt
    draw.rectangle([370, 520, 430, 640], fill=(215, 175, 145)) # Neck
    # Head
    draw.ellipse([290, 260, 510, 560], fill=(225, 185, 155)) # Face
    # Hair mass
    draw.chord([270, 200, 530, 420], 180, 360, fill=(35, 25, 20))
    # Hair strands / fringes for edge detail testing
    for x_offset in range(-60, 70, 8):
        draw.line([(400 + x_offset, 210), (400 + x_offset * 1.2, 180)], fill=(35, 25, 20), width=3)

    img.save(filepath, format="JPEG", quality=95)
    return img


def run_evaluation_suite():
    print("=" * 60)
    print("Snap2Print Phase 1: Quality Refinement & Benchmark Test")
    print("=" * 60)

    eval_dir = BASE_DIR / "tests" / "evaluation_results"
    eval_dir.mkdir(parents=True, exist_ok=True)

    input_path = BASE_DIR / "tests" / "test_portrait.jpg"
    if not input_path.exists():
        create_realistic_evaluation_portrait(input_path)

    img = Image.open(input_path).convert("RGB")
    original_size = img.size
    print(f"[1] Loaded evaluation image: {input_path.name} | Resolution: {original_size[0]}x{original_size[1]}")

    # 1. Model inference
    t0 = time.time()
    remover = get_background_remover()
    raw_mask, model_meta = remover.segment_mask(img)
    t_model = int((time.time() - t0) * 1000)
    print(f"[2] Model: {model_meta['model_name']} | Raw Mask Generated in: {t_model} ms")

    # Save raw mask
    Image.fromarray(raw_mask).save(eval_dir / "01_raw_mask.png")

    # 2. Refinement & Spill Suppression (Auto Cleanup)
    t1 = time.time()
    rgb_np = np.array(img)
    refined_mask = refine_mask_edges(raw_mask, guide_img=rgb_np, smoothness=1.0)
    cleaned_rgb = suppress_color_spill(rgb_np, refined_mask)
    t_refine = int((time.time() - t1) * 1000)
    print(f"[3] Mask Refinement & Color Decontamination completed in: {t_refine} ms")

    # Save refined mask
    Image.fromarray(refined_mask).save(eval_dir / "02_refined_mask.png")

    # 3. Quality evaluation
    quality = evaluate_mask_quality(refined_mask)
    print(f"[4] Quality Assessment Heuristic: {quality['status']} ({quality['reason']})")

    # 4. Compositing on requested studio backgrounds
    t2 = time.time()
    foreground = Image.fromarray(cleaned_rgb)
    transparent_rgba = apply_alpha_to_image(foreground, refined_mask)
    transparent_rgba.save(eval_dir / "03_transparent.png")

    white_bg = composite_on_background(transparent_rgba, bg_type="white")
    white_bg.save(eval_dir / "04_studio_white.png")

    blue_bg = composite_on_background(transparent_rgba, bg_type="blue")
    blue_bg.save(eval_dir / "05_passport_blue.png")

    custom_bg = composite_on_background(transparent_rgba, bg_type="custom", custom_hex="#ff7700")
    custom_bg.save(eval_dir / "06_custom_color.png")
    t_comp = int((time.time() - t2) * 1000)
    print(f"[5] Composited 4 studio background variations in: {t_comp} ms")

    total_time = t_model + t_refine + t_comp
    print("-" * 60)
    print(f"Total Execution Time: {total_time} ms")
    print(f"Timing Breakdown:")
    print(f"  • Model Inference : {t_model} ms")
    print(f"  • Edge Refinement : {t_refine} ms")
    print(f"  • Multi Compositing: {t_comp} ms")
    print(f"All evaluation outputs saved to: {eval_dir}")
    print("=" * 60)


if __name__ == "__main__":
    run_evaluation_suite()
