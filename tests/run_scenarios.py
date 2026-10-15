"""
Multi-Scenario Evaluation Suite for Snap2Print Phase 1.
Generates and benchmarks all 8 test scenarios:
1. Green background (Chroma Key)
2. Blue background (Chroma Key)
3. White background (Chroma Key)
4. Uneven / Complex background (AI U2NetP Fallback)
5. Hair with fine detail / wisps
6. Glasses & facial contours
7. Dark clothing against light background
8. Light clothing against studio background

For each scenario, saves:
- original.png
- raw_mask.png
- refined_mask.png
- final_result.png
"""
import sys
import time
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.services.background_analyzer import analyze_background
from backend.services.chroma_key import segment_chroma_key
from backend.services.background_removal import get_background_remover
from backend.services.mask_refinement import refine_hybrid_mask
from backend.services.image_compositor import apply_mask_to_foreground, composite_studio_background


def generate_scenario_image(scenario_name: str, width: int = 600, height: int = 800) -> Image.Image:
    """Generates synthetic portrait tailored to specific edge conditions."""
    if scenario_name == "green_bg":
        bg_color = (40, 180, 60)
        suit_color = (30, 45, 75)
    elif scenario_name == "blue_bg":
        bg_color = (30, 100, 220)
        suit_color = (40, 40, 40)
    elif scenario_name == "white_bg":
        bg_color = (250, 250, 252)
        suit_color = (25, 30, 45)
    elif scenario_name == "uneven_bg":
        # Complex multi-color gradient wall
        img = Image.new("RGB", (width, height), color=(140, 100, 80))
        draw = ImageDraw.Draw(img)
        for y in range(height):
            c = (int(100 + 100 * (y / height)), int(60 + 80 * (y / height)), 120)
            draw.line([(0, y), (width, y)], fill=c)
        bg_color = None
        suit_color = (40, 60, 90)
    elif scenario_name == "dark_clothing":
        bg_color = (240, 240, 245)
        suit_color = (15, 18, 22) # Very dark suit
    elif scenario_name == "light_clothing":
        bg_color = (60, 140, 230)
        suit_color = (240, 240, 245) # White shirt against blue
    elif scenario_name == "fine_hair":
        bg_color = (45, 175, 75)
        suit_color = (35, 45, 65)
    elif scenario_name == "glasses":
        bg_color = (50, 160, 220)
        suit_color = (30, 35, 50)
    else:
        bg_color = (180, 220, 240)
        suit_color = (40, 60, 90)

    if bg_color:
        img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Torso / Suit
    draw.polygon([(120, height), (240, 480), (360, 480), (480, height)], fill=suit_color)
    # Neck
    draw.rectangle([275, 400, 325, 490], fill=(225, 185, 155))
    # Head
    draw.ellipse([215, 200, 385, 430], fill=(235, 195, 165))
    # Hair mass
    draw.chord([200, 150, 400, 310], 180, 360, fill=(35, 25, 20))

    if scenario_name == "fine_hair":
        # Extra fine hair strands
        for xo in range(-60, 70, 6):
            draw.line([(300 + xo, 165), (300 + int(xo * 1.3), 130)], fill=(35, 25, 20), width=2)

    if scenario_name == "glasses":
        # Spectacles frame
        draw.rectangle([240, 280, 285, 315], outline=(15, 15, 15), width=3)
        draw.rectangle([315, 280, 360, 315], outline=(15, 15, 15), width=3)
        draw.line([(285, 295), (315, 295)], fill=(15, 15, 15), width=3)

    return img


def run_benchmark():
    print("=" * 65)
    print("Snap2Print Phase 1: Hybrid Evaluation & Benchmark Suite")
    print("=" * 65)

    base_eval_dir = BASE_DIR / "tests" / "scenarios"
    base_eval_dir.mkdir(parents=True, exist_ok=True)

    scenarios = [
        "green_bg",
        "blue_bg",
        "white_bg",
        "uneven_bg",
        "fine_hair",
        "glasses",
        "dark_clothing",
        "light_clothing"
    ]

    remover = get_background_remover() # Prewarm singleton

    for sc in scenarios:
        sc_dir = base_eval_dir / sc
        sc_dir.mkdir(parents=True, exist_ok=True)

        img = generate_scenario_image(sc)
        img.save(sc_dir / "original.png")

        rgb_np = np.array(img)

        # 1. Analyze
        t0 = time.time()
        analysis = analyze_background(rgb_np)
        method = analysis["recommended_method"]

        # 2. Segment
        if method == "chroma_key":
            raw_mask, despilled_rgb = segment_chroma_key(
                rgb_img=rgb_np,
                target_color_rgb=analysis["estimated_color_rgb"],
                tolerance=0.28,
                softness=0.12,
                protect_skin=True
            )
            working_rgb = despilled_rgb
        else:
            raw_mask, _ = remover.segment_mask(img)
            working_rgb = rgb_np
        t_seg = int((time.time() - t0) * 1000)

        # 3. Refine
        t1 = time.time()
        refined_mask = refine_hybrid_mask(raw_mask, guide_img=working_rgb, smoothness=1.0)
        t_refine = int((time.time() - t1) * 1000)

        # 4. Composite on Studio Blue
        foreground = Image.fromarray(working_rgb)
        transparent = apply_mask_to_foreground(foreground, refined_mask)
        final_result = composite_studio_background(transparent, bg_type="blue")

        # Save artifacts
        Image.fromarray(raw_mask).save(sc_dir / "raw_mask.png")
        Image.fromarray(refined_mask).save(sc_dir / "refined_mask.png")
        final_result.save(sc_dir / "final_result.png")

        print(f"[{sc}] Method: {method.upper()} | Seg: {t_seg}ms | Refine: {t_refine}ms | Artifacts saved.")

    print("-" * 65)
    print(f"All 8 benchmark test scenarios saved cleanly to: {base_eval_dir}")
    print("=" * 65)


if __name__ == "__main__":
    run_benchmark()
