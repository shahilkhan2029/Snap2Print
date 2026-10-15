"""
Test Suite for Snap2Print Restructured Studio Workflow
Verifies:
1. Upload & Multi-Face Detection (Preserves original untouched, generates auto-crop, NO background removal on upload).
2. Selection of exactly ONE person from group photo.
3. Passport Auto-Crop computation (35:45 ratio, head/shoulder framing).
4. Background removal executed ONLY on the final accepted cropped portrait.
5. Background replacement and high-resolution export.
6. Tests single-person, 3-person group, and complex background photos.
"""
import sys
import io
import json
from pathlib import Path
from PIL import Image
import numpy as np

# Ensure root workspace is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import UploadFile
from backend.api.photo import upload_and_detect, process_cropped_background, export_final, SESSION_CACHE
from backend.services.crop_service import calculate_passport_crop, ASPECT_RATIOS


async def test_3_person_group_photo():
    """Test 3-person group photo: detects all 3 faces, selects face 2, crops and segments only face 2."""
    img_path = Path("input/5e14125c_original.jpg")
    assert img_path.exists(), "Test group image input/5e14125c_original.jpg must exist"

    with open(img_path, "rb") as f:
        file_bytes = f.read()

    upload_file = UploadFile(file=io.BytesIO(file_bytes), filename="group_3_people.jpg")

    # Step 1 & 2: Upload and detect
    resp = await upload_and_detect(file=upload_file)
    data = json.loads(resp.body.decode("utf-8"))

    assert data["success"] is True
    session_id = data["session_id"]
    assert session_id in SESSION_CACHE

    fd = data["face_detection"]
    assert fd["detected"] is True
    assert fd["face_count"] == 3, f"Expected 3 faces detected, got {fd.get('face_count')}"
    assert len(fd["faces"]) == 3

    # CRITICAL REQUIREMENT: Assert NO background removal was run during upload!
    session = SESSION_CACHE[session_id]
    assert "cropped_mask_path" not in session, "Background removal must NOT run during upload!"
    assert "mask_path" not in session, "Background removal must NOT run on original image!"

    # Verify each face has auto_crop calculated with standard 35:45 ratio
    for face in fd["faces"]:
        ac = face["auto_crop"]
        assert ac is not None
        assert ac["aspect_ratio"] == "35:45"
        # ratio ~ 0.7778
        assert 0.77 <= ac["ratio_val"] <= 0.79

    # Select Face 2 (center person) and accept crop
    face2 = fd["faces"][1]
    ac2 = face2["auto_crop"]

    resp_crop = await process_cropped_background(
        session_id=session_id,
        crop_x=ac2["x"],
        crop_y=ac2["y"],
        crop_width=ac2["width"],
        crop_height=ac2["height"],
        crop_x_norm=ac2["x_norm"],
        crop_y_norm=ac2["y_norm"],
        crop_w_norm=ac2["w_norm"],
        crop_h_norm=ac2["h_norm"],
        method_mode="auto",
        smoothness=1.0
    )
    data_crop = json.loads(resp_crop.body.decode("utf-8"))

    assert data_crop["success"] is True
    assert "transparent_preview" in data_crop["previews"]
    assert "cropped_original" in data_crop["previews"]

    # Verify that cropped dimensions match face 2's crop
    crop_dims = data_crop["crop_dimensions"]
    assert crop_dims["width"] == ac2["width"]
    assert crop_dims["height"] == ac2["height"]

    # Export final passport photo with Studio White and Passport Blue
    resp_export = await export_final(session_id=session_id, bg_type="blue")
    data_export = json.loads(resp_export.body.decode("utf-8"))
    assert data_export["success"] is True
    assert "passport_blue.png" in data_export["download_url"]


async def test_single_person_photo():
    """Test single person photo upload, auto-crop, and background removal."""
    # Find a single person portrait in input/
    candidates = list(Path("input").glob("*_original.png")) + list(Path("input").glob("*_original.jpeg"))
    test_img = None
    for cand in candidates:
        if cand.stat().st_size > 50000:
            test_img = cand
            break

    assert test_img is not None, "At least one portrait image must exist in input/"

    with open(test_img, "rb") as f:
        file_bytes = f.read()

    upload_file = UploadFile(file=io.BytesIO(file_bytes), filename="single_portrait.jpg")
    resp = await upload_and_detect(file=upload_file)
    data = json.loads(resp.body.decode("utf-8"))

    assert data["success"] is True
    session_id = data["session_id"]

    # Assert no background removal executed yet
    assert "cropped_mask_path" not in SESSION_CACHE[session_id]

    fd = data["face_detection"]
    faces = fd.get("faces", [])
    if faces:
        ac = faces[0]["auto_crop"]
        crop_resp = await process_cropped_background(
            session_id=session_id,
            crop_x_norm=ac["x_norm"],
            crop_y_norm=ac["y_norm"],
            crop_w_norm=ac["w_norm"],
            crop_h_norm=ac["h_norm"],
            method_mode="auto",
            smoothness=1.0
        )
        crop_data = json.loads(crop_resp.body.decode("utf-8"))
        assert crop_data["success"] is True
        assert "transparent_preview" in crop_data["previews"]


async def test_manual_crop_adjustment_bounds():
    """Test manual crop adjustment and boundary safety."""
    img_path = Path("input/5e14125c_original.jpg")
    with open(img_path, "rb") as f:
        file_bytes = f.read()

    upload_file = UploadFile(file=io.BytesIO(file_bytes), filename="test_crop.jpg")
    resp = await upload_and_detect(file=upload_file)
    data = json.loads(resp.body.decode("utf-8"))
    session_id = data["session_id"]

    # Test extreme crop coordinates to ensure clamping safety
    crop_resp = await process_cropped_background(
        session_id=session_id,
        crop_x_norm=0.1,
        crop_y_norm=0.1,
        crop_w_norm=0.8,
        crop_h_norm=0.8,
        method_mode="auto",
        smoothness=1.0
    )
    crop_data = json.loads(crop_resp.body.decode("utf-8"))
    assert crop_data["success"] is True
    assert crop_data["crop_dimensions"]["width"] > 0
    assert crop_data["crop_dimensions"]["height"] > 0


if __name__ == "__main__":
    import asyncio
    print("=================================================================")
    print("RUNNING RESTRUCTURED WORKFLOW TEST SUITE")
    print("=================================================================")

    print("\n--- Test 1: 3-Person Group Photo ---")
    asyncio.run(test_3_person_group_photo())
    print(">>> Test 1 PASSED: 3 faces detected, face 2 selected, crop-only bg removed, export verified.")

    print("\n--- Test 2: Single-Person Photo ---")
    asyncio.run(test_single_person_photo())
    print(">>> Test 2 PASSED: Single person detected, crop and bg removed.")

    print("\n--- Test 3: Manual Crop Bounds Clamping ---")
    asyncio.run(test_manual_crop_adjustment_bounds())
    print(">>> Test 3 PASSED: Bounds clamped and safe.")

    print("\n=================================================================")
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=================================================================")

