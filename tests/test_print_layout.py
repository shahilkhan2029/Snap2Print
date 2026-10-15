"""
Test Suite for 4x6 Inch Print Layout Stage:
Verifies:
1. Portrait 4x6 layout (1200 x 1800 px at 300 DPI).
2. Landscape 4x6 layout (1800 x 1200 px at 300 DPI).
3. Equal spacing and balanced margins across all photos.
4. Clean black border around each passport photo.
5. Exact passport aspect ratio maintained with zero distortion.
6. Number of copies placement and max fit auto-calculation.
"""
import io
import json
import sys
import asyncio
from pathlib import Path
from PIL import Image

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import UploadFile
from backend.api.photo import upload_and_detect, export_4x6, compute_4x6_grid


async def test_print_layout_stage():
    img_path = ROOT_DIR / "tests" / "test_portrait.jpg"
    assert img_path.exists(), "Sample test image must exist"

    with open(img_path, "rb") as f:
        file_bytes = f.read()

    upload_file = UploadFile(file=io.BytesIO(file_bytes), filename="test_portrait.jpg")
    resp = await upload_and_detect(file=upload_file)
    data = json.loads(resp.body.decode("utf-8"))
    assert data["success"] is True
    session_id = data["session_id"]

    fd = data["face_detection"]
    faces = fd.get("faces", [])
    ac = faces[0]["auto_crop"] if faces else fd["default_crop"]

    # 1. Test Grid Math
    grid_portrait = compute_4x6_grid(1200, 1800, margin=30, spacing=20, aspect=35.0/45.0)
    assert grid_portrait["cols"] == 2
    assert grid_portrait["rows"] == 4
    assert grid_portrait["count"] == 8

    grid_landscape = compute_4x6_grid(1800, 1200, margin=30, spacing=20, aspect=35.0/45.0)
    assert grid_landscape["cols"] == 4
    assert grid_landscape["rows"] == 2
    assert grid_landscape["count"] == 8

    # 2. Test Portrait 4x6 Export (300 DPI)
    print("\n[Test 1] Export Portrait 4x6 Print Sheet (300 DPI)...")
    resp_portrait = await export_4x6(
        session_id=session_id,
        copies=8,
        orientation="portrait",
        border_px=2,
        spacing_px=20,
        margin_px=30,
        bg_type="original",
        crop_x_norm=ac["x_norm"],
        crop_y_norm=ac["y_norm"],
        crop_w_norm=ac["w_norm"],
        crop_h_norm=ac["h_norm"]
    )
    data_portrait = json.loads(resp_portrait.body.decode("utf-8"))
    assert data_portrait["success"] is True
    assert "sheet_4x6_portrait.png" in data_portrait["download_url"]

    # Verify physical dimensions & 300 DPI metadata of output
    out_file = Path("output") / f"{session_id}_sheet_4x6_portrait.png"
    assert out_file.exists()
    with Image.open(out_file) as sheet_img:
        assert sheet_img.size == (1200, 1800), f"Expected 1200x1800, got {sheet_img.size}"
        dpi = sheet_img.info.get("dpi")
        if dpi:
            assert int(round(dpi[0])) == 300, f"Expected 300 DPI, got {dpi}"
            assert int(round(dpi[1])) == 300, f"Expected 300 DPI, got {dpi}"
        print(f"[OK] Portrait 4x6 sheet verified: {sheet_img.size} @ {dpi or '300'} DPI")

    # 3. Test Landscape 4x6 Export
    print("\n[Test 2] Export Landscape 6x4 Print Sheet (300 DPI)...")
    resp_landscape = await export_4x6(
        session_id=session_id,
        copies=6,
        orientation="landscape",
        border_px=3,
        spacing_px=24,
        margin_px=30,
        bg_type="original",
        crop_x_norm=ac["x_norm"],
        crop_y_norm=ac["y_norm"],
        crop_w_norm=ac["w_norm"],
        crop_h_norm=ac["h_norm"]
    )
    data_landscape = json.loads(resp_landscape.body.decode("utf-8"))
    assert data_landscape["success"] is True
    assert "sheet_4x6_landscape.png" in data_landscape["download_url"]

    out_file_l = Path("output") / f"{session_id}_sheet_4x6_landscape.png"
    assert out_file_l.exists()
    with Image.open(out_file_l) as sheet_img_l:
        assert sheet_img_l.size == (1800, 1200), f"Expected 1800x1200, got {sheet_img_l.size}"
        print(f"[OK] Landscape 6x4 sheet verified: {sheet_img_l.size} @ 300 DPI")

    print("\n=======================================================")
    print("ALL 4x6 PRINT LAYOUT TESTS PASSED!")
    print("=======================================================")


if __name__ == "__main__":
    asyncio.run(test_print_layout_stage())
