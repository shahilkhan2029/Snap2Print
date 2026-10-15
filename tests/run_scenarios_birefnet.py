"""
Comprehensive 10-Scenario Benchmark Suite:
Compares BiRefNet-Portrait vs U2NetP vs Chroma Key across all 10 conditions:
1. Green background
2. Blue background
3. White background
4. Complex / Uneven background
5. Fine hair detail / wisps
6. Dark hair against dark background
7. Dark clothing against light background
8. Light clothing against light background
9. Glasses & facial contours
10. Uneven lighting / shadow gradients

For each test scenario, saves:
- original.png
- birefnet_raw_mask.png
- birefnet_refined_mask.png
- birefnet_final.png
- u2netp_final.png
- chroma_key_final.png
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
from backend.services.birefnet_portrait import get_birefnet_remover
from backend.services.mask_refinement import refine_hybrid_mask
from backend.services.image_compositor import apply_mask_to_foreground, composite_studio_background


def generate_benchmark_portrait(scenario_name: str, width: int = 600, height: int = 800) -> Image.Image:
    """Generates synthetic portraits tailored for precision studio evaluation."""
    # Defaults
    bg_color = (240, 240, 245)
    suit_color = (40, 50, 75)
    hair_color = (35, 25, 20)
    has_fine_hair = False
    has_glasses = False
    is_gradient_bg = False

    if scenario_name == "01_green_bg":
        bg_color = (35, 175, 55)
    elif scenario_name == "02_blue_bg":
        bg_color = (30, 110, 230)
    elif scenario_name == "03_white_bg":
        bg_color = (252, 252, 255)
    elif scenario_name == "04_complex_bg":
        is_gradient_bg = True
    elif scenario_name == "05_fine_hair":
        bg_color = (190, 215, 235)
        has_fine_hair = True
    elif scenario_name == "06_dark_hair":
        bg_color = (55, 60, 70) # Dark grey wall
        hair_color = (15, 15, 15) # Very dark hair
    elif scenario_name == "07_dark_clothing":
        bg_color = (250, 250, 252)
        suit_color = (12, 14, 18) # Deep black suit
    elif scenario_name == "08_light_clothing":
        bg_color = (235, 235, 240)
        suit_color = (245, 245, 250) # White shirt against light wall
    elif scenario_name == "09_glasses":
        bg_color = (180, 220, 245)
        has_glasses = True
    elif scenario_name == "10_uneven_lighting":
        is_gradient_bg = True

    if is_gradient_bg:
        img = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(img)
        for y in range(height):
            c = (int(80 + 120 * (y / height)), int(90 + 60 * (y / height)), int(140 - 50 * (y / height)))
            draw.line([(0, y), (width, y)], fill=c)
    else:
        img = Image.new("RGB", (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)

    # Torso / Suit
    draw.polygon([(110, height), (230, 480), (370, 480), (490, height)], fill=suit_color)
    # Neck
    draw.rectangle([275, 400, 325, 490], fill=(225, 185, 155))
    # Head
    draw.ellipse([215, 200, 385, 430], fill=(235, 195, 165))
    # Hair mass
    draw.chord([200, 150, 400, 310], 180, 360, fill=hair_color)

    if has_fine_hair:
        for xo in range(-65, 75, 6):
            draw.line([(300 + xo, 165), (300 + int(xo * 1.3), 125)], fill=hair_color, width=2)

    if has_glasses:
        draw.rectangle([240, 280, 285, 315], outline=(15, 15, 15), width=3)
        draw.rectangle([315, 280, 360, 315], outline=(15, 15, 15), width=3)
        draw.line([(285, 295), (315, 295)], fill=(15, 15, 15), width=3)

    return img


def run_benchmark():
    print("=" * 75)
    print("Snap2Print Phase 1: BiRefNet-Portrait vs U2NetP vs Chroma Key Benchmark")
    print("=" * 75)

    base_dir = BASE_DIR / "tests" / "scenarios_birefnet"
    base_dir.mkdir(parents=True, exist_ok=True)

    scenarios = [
        "01_green_bg",
        "02_blue_bg",
        "03_white_bg",
        "04_complex_bg",
        "05_fine_hair",
        "06_dark_hair",
        "07_dark_clothing",
        "08_light_clothing",
        "09_glasses",
        "10_uneven_lighting"
    ]

    print("Pre-warming model sessions...")
    birefnet = get_birefnet_remover()
    u2netp = get_background_remover()

    results_table = []

    for sc in scenarios:
        sc_folder = base_dir / sc
        sc_folder.mkdir(parents=True, exist_ok=True)

        img = generate_benchmark_portrait(sc)
        img.save(sc_folder / "original.png")
        rgb_np = np.array(img)

        # 1. BiRefNet-Portrait
        t0 = time.time()
        b_raw_mask, _ = birefnet.segment_mask(img)
        b_ref_mask = refine_hybrid_mask(b_raw_mask, rgb_np, smoothness=1.0)
        b_trans = apply_mask_to_foreground(img, b_ref_mask)
        b_final = composite_studio_background(b_trans, bg_type="blue")
        t_birefnet = int((time.time() - t0) * 1000)

        Image.fromarray(b_raw_mask).save(sc_folder / "birefnet_raw_mask.png")
        Image.fromarray(b_ref_mask).save(sc_folder / "birefnet_refined_mask.png")
        b_final.save(sc_folder / "birefnet_final.png")

        # 2. U2NetP
        t0 = time.time()
        u_raw_mask, _ = u2netp.segment_mask(img)
        u_ref_mask = refine_hybrid_mask(u_raw_mask, rgb_np, smoothness=1.0)
        u_trans = apply_mask_to_foreground(img, u_ref_mask)
        u_final = composite_studio_background(u_trans, bg_type="blue")
        t_u2netp = int((time.time() - t0) * 1000)
        u_final.save(sc_folder / "u2netp_final.png")

        # 3. Chroma Key
        t0 = time.time()
        bg_analysis = analyze_background(rgb_np)
        c_raw_mask, c_despilled = segment_chroma_key(
            rgb_img=rgb_np,
            target_color_rgb=bg_analysis["estimated_color_rgb"],
            tolerance=0.28,
            softness=0.12,
            protect_skin=True
        )
        c_ref_mask = refine_hybrid_mask(c_raw_mask, c_despilled, smoothness=1.0)
        c_trans = apply_mask_to_foreground(Image.fromarray(c_despilled), c_ref_mask)
        c_final = composite_studio_background(c_trans, bg_type="blue")
        t_chroma = int((time.time() - t0) * 1000)
        c_final.save(sc_folder / "chroma_key_final.png")

        # Recommendation in Auto
        auto_selected = "Chroma Key" if (bg_analysis["is_uniform"] and bg_analysis["detected_color"] in ("green", "blue")) else "BiRefNet-Portrait"

        results_table.append({
            "scenario": sc,
            "birefnet_ms": t_birefnet,
            "u2netp_ms": t_u2netp,
            "chroma_ms": t_chroma,
            "auto_choice": auto_selected
        })

        print(f"[{sc}] BiRefNet: {t_birefnet}ms | U2NetP: {t_u2netp}ms | Chroma: {t_chroma}ms | Auto: {auto_selected}")

    print("\n" + "=" * 75)
    print("BENCHMARK SUMMARY:")
    print(f"{'Scenario':<22} | {'BiRefNet (ms)':<14} | {'U2NetP (ms)':<12} | {'Chroma (ms)':<12} | {'Auto Choice'}")
    print("-" * 75)
    for r in results_table:
        print(f"{r['scenario']:<22} | {r['birefnet_ms']:<14} | {r['u2netp_ms']:<12} | {r['chroma_ms']:<12} | {r['auto_choice']}")
    print("=" * 75)
    print(f"All 10 benchmark artifacts saved to: {base_dir}")


if __name__ == "__main__":
    run_benchmark()
