"""
Lightweight background analyzer.
Samples the perimeter / corner border regions of a portrait
to determine if the background is sufficiently uniform (e.g., green screen,
studio blue, pure white backdrop, or solid wall).

Returns:
- is_uniform: bool (True -> recommend Chroma Key, False -> recommend AI U2NetP)
- estimated_color_rgb: Tuple[int, int, int]
- estimated_color_name: str ('green', 'blue', 'white', 'other', or 'none')
- uniformity_score: float (0.0 to 1.0, where 1.0 is perfectly flat color)
- details: dict for debug telemetry
"""
import cv2
import numpy as np
from typing import Tuple, Dict, Any


def analyze_background(rgb_img: np.ndarray) -> Dict[str, Any]:
    """
    Analyzes image border regions (outer 8% perimeter) where customer portraits
    consistently show the background backdrop, avoiding central subject pixels.
    """
    h, w = rgb_img.shape[:2]
    border_px_y = max(int(h * 0.08), 8)
    border_px_x = max(int(w * 0.08), 8)

    # Sample top strip, top-left, top-right, left strip, right strip
    # Avoid bottom where shoulders/torso rest
    top_strip = rgb_img[0:border_px_y, :]
    left_strip = rgb_img[border_px_y:int(h * 0.6), 0:border_px_x]
    right_strip = rgb_img[border_px_y:int(h * 0.6), w - border_px_x:w]

    # Reshape and concatenate sampled perimeter pixels
    samples = np.vstack([
        top_strip.reshape(-1, 3),
        left_strip.reshape(-1, 3),
        right_strip.reshape(-1, 3)
    ])

    # Convert sampled pixels to HSV and float RGB
    samples_float = samples.astype(np.float32)
    mean_rgb = np.median(samples_float, axis=0) # Median is robust against localized hair wisps
    std_rgb = np.std(samples_float, axis=0)
    avg_std = float(np.mean(std_rgb))

    # Uniformity score: standard deviation < 12 is extremely flat (~0.9-1.0),
    # > 45 is non-uniform / textured / complex (~ < 0.4)
    uniformity_score = float(np.clip(1.0 - (avg_std / 45.0), 0.0, 1.0))

    # Detect color category in HSV
    sample_img_1px = np.uint8([[mean_rgb]])
    hsv_sample = cv2.cvtColor(sample_img_1px, cv2.COLOR_RGB2HSV)[0, 0]
    hue, sat, val = int(hsv_sample[0]), int(hsv_sample[1]), int(hsv_sample[2])

    detected_color = "other"
    is_chroma_candidate = False

    # 1. Green screen (Hue roughly 35 - 85 in OpenCV's 0-180 scale, Sat > 50, Val > 50)
    if 35 <= hue <= 85 and sat >= 45 and val >= 45:
        detected_color = "green"
        is_chroma_candidate = True

    # 2. Studio Blue (Hue roughly 90 - 130, Sat > 45, Val > 45)
    elif 90 <= hue <= 130 and sat >= 45 and val >= 45:
        detected_color = "blue"
        is_chroma_candidate = True

    # 3. Studio White / High-Key (Sat < 25, Val > 200, low variance)
    elif sat <= 25 and val >= 195:
        detected_color = "white"
        is_chroma_candidate = True

    # 4. Other solid studio backdrop (uniformity_score > 0.85 and low std dev)
    elif uniformity_score >= 0.85 and avg_std < 8.0:
        detected_color = "uniform_solid"
        is_chroma_candidate = True

    # Final decision threshold:
    # Must be a recognized chroma/backdrop color and have high uniformity (score >= 0.72)
    is_suitable = bool(is_chroma_candidate and (uniformity_score >= 0.72))

    return {
        "is_uniform": is_suitable,
        "recommended_method": "chroma_key" if is_suitable else "u2netp",
        "detected_color": detected_color,
        "estimated_color_rgb": (int(mean_rgb[0]), int(mean_rgb[1]), int(mean_rgb[2])),
        "hsv_signature": (hue, sat, val),
        "uniformity_score": round(uniformity_score, 3),
        "color_std_dev": round(avg_std, 2)
    }
