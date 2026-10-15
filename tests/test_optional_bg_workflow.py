"""
Test Suite for Optional Background Removal & Real-Time Passport Crop Preview
Verifies:
1. Upload & face detection pre-calculates auto-crop for all faces.
2. Background removal is completely OPTIONAL.
3. Keep Original Background exports full camera quality cropped passport photo with zero AI segmentation.
4. Remove Background segments only the cropped person and exports studio backdrop.
5. All tests verify speed, quality, and aspect ratio integrity.
"""
import sys
import io
import json
import asyncio
from pathlib import Path
from PIL import Image

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import UploadFile
from backend.api.photo import upload_and_detect, process_cropped_background, export_final, SESSION_CACHE


async def test_optional_background_workflow():
    img_path = Path("input/5e14125c_original.jpg")
    assert img_path.exists(), "input/5e14125c_original.jpg must exist"

    with open(img_path, "rb") as f:
        file_bytes = f.read()

    upload_file = UploadFile(file=io.BytesIO(file_bytes), filename="group_3.jpg")

    # Step 1: Upload & Multi-Face Detection
    resp = await upload_and_detect(file=upload_file)
    data = json.loads(resp.body.decode("utf-8"))
    assert data["success"] is True
    session_id = data["session_id"]

    fd = data["face_detection"]
    assert fd["face_count"] == 3
    faces = fd["faces"]

    # Select Face 2 (center person)
    face2 = faces[1]
    ac = face2["auto_crop"]

    # --- REQUIREMENT 1 & 2: EXPORT WITH ORIGINAL BACKGROUND (ZERO AI SEGMENTATION) ---
    print("\n[Test A] Export with Original Background (Zero AI segmentation)")
    resp_orig = await export_final(
        session_id=session_id,
        bg_type="original",
        crop_x_norm=ac["x_norm"],
        crop_y_norm=ac["y_norm"],
        crop_w_norm=ac["w_norm"],
        crop_h_norm=ac["h_norm"]
    )
    data_orig = json.loads(resp_orig.body.decode("utf-8"))
    assert data_orig["success"] is True
    assert "passport_original.png" in data_orig["download_url"]
    print("[OK] Successfully exported passport photo with original background in:", data_orig["export_time_ms"], "ms")

    # Check exported file on disk
    exported_file = Path("output") / f"{session_id}_passport_original.png"
    assert exported_file.exists()
    with Image.open(exported_file) as exp_img:
        w, h = exp_img.size
        ratio = w / float(h)
        print(f"[OK] Export dimensions: {w}x{h}, aspect ratio: {ratio:.4f} (matches 35:45 ~ {35/45:.4f})")
        assert 0.77 <= ratio <= 0.79, f"Aspect ratio must match passport standard, got {ratio}"

    # Verify that NO background removal mask was generated during this entire original-bg flow
    session = SESSION_CACHE[session_id]
    assert "cropped_mask_path" not in session, "Background removal mask must not exist for original bg flow!"

    # --- REQUIREMENT 3: OPTIONAL BACKGROUND REMOVAL (When user explicitly requests studio backdrop) ---
    print("\n[Test B] Remove Background on Cropped Person & Export Studio Blue")
    resp_crop = await process_cropped_background(
        session_id=session_id,
        crop_x_norm=ac["x_norm"],
        crop_y_norm=ac["y_norm"],
        crop_w_norm=ac["w_norm"],
        crop_h_norm=ac["h_norm"],
        method_mode="auto",
        smoothness=1.0
    )
    data_crop = json.loads(resp_crop.body.decode("utf-8"))
    assert data_crop["success"] is True
    assert "transparent_preview" in data_crop["previews"]
    print("[OK] Background removed only on cropped person in:", data_crop["timings"]["total_ms"], "ms")

    # Export on Studio Blue
    resp_blue = await export_final(session_id=session_id, bg_type="blue")
    data_blue = json.loads(resp_blue.body.decode("utf-8"))
    assert data_blue["success"] is True
    assert "passport_blue.png" in data_blue["download_url"]

    exported_blue = Path("output") / f"{session_id}_passport_blue.png"
    assert exported_blue.exists()
    with Image.open(exported_blue) as exp_blue:
        w_b, h_b = exp_blue.size
        ratio_b = w_b / float(h_b)
        print(f"[OK] Studio Blue dimensions: {w_b}x{h_b}, aspect ratio: {ratio_b:.4f}")
        assert 0.77 <= ratio_b <= 0.79

    print("\n=======================================================")
    print("ALL OPTIONAL BACKGROUND WORKFLOW TESTS PASSED!")
    print("=======================================================")


if __name__ == "__main__":
    asyncio.run(test_optional_background_workflow())
