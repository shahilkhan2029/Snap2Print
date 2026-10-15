import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.services.background_removal import get_background_remover, composite_background


def create_dummy_portrait(path: Path):
    """Generates a synthetic portrait image to test pipeline without requiring external assets."""
    img = Image.new("RGB", (600, 800), color=(180, 220, 240))
    draw = ImageDraw.Draw(img)

    # Draw body / shoulders
    draw.ellipse([150, 480, 450, 950], fill=(40, 60, 90))

    # Draw neck
    draw.rectangle([270, 420, 330, 520], fill=(230, 190, 160))

    # Draw head
    draw.ellipse([210, 200, 390, 440], fill=(240, 200, 170))

    # Draw hair
    draw.chord([200, 160, 400, 320], 180, 360, fill=(30, 20, 15))

    img.save(path, format="JPEG", quality=95)
    print(f"Created synthetic portrait at {path}")
    return img


def test_pipeline():
    print("Testing Phase 1 Background Removal Pipeline...")
    dummy_input = BASE_DIR / "tests" / "test_portrait.jpg"
    dummy_input.parent.mkdir(parents=True, exist_ok=True)

    img = create_dummy_portrait(dummy_input)

    print("Loading model session...")
    remover = get_background_remover()

    print("Running background removal inference...")
    transparent_img = remover.remove_background(img)
    assert transparent_img.mode == "RGBA", "Output must be RGBA"
    print(f"Transparent image generated successfully: {transparent_img.size}, mode: {transparent_img.mode}")

    print("Testing compositing backgrounds...")
    white_bg = composite_background(transparent_img, bg_type="white")
    assert white_bg.size == transparent_img.size, "Size must match"
    print("Composited white background successfully.")

    blue_bg = composite_background(transparent_img, bg_type="blue")
    assert blue_bg.size == transparent_img.size, "Size must match"
    print("Composited blue background successfully.")

    custom_bg = composite_background(transparent_img, bg_type="custom", custom_hex="#ff9900")
    assert custom_bg.size == transparent_img.size, "Size must match"
    print("Composited custom color background successfully.")

    print("\nALL PIPELINE TESTS PASSED!")


if __name__ == "__main__":
    test_pipeline()
