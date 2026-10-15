"""
Color-distance and tolerance-based Chroma Key segmentation service.
Designed for CPU execution.
Features:
- HSV hue+saturation distance (more robust than RGB for green/blue screens)
- Multi-color support (green, blue, studio white, custom solid)
- Human skin protection mask (prevents skin pixels from being keyed out)
- Edge spill suppression around hair and clothing
- Morphological hole fill for clean interior
"""
import cv2
import numpy as np
from typing import Tuple, Dict, Any, Optional


def create_skin_protection_mask(rgb_img: np.ndarray) -> np.ndarray:
    """
    Detects natural human skin tones across diverse complexions using
    combined YCrCb and HSV color spaces.
    Returns uint8 mask (255 = skin protected, 0 = non-skin).
    """
    # 1. YCrCb check (very robust across different skin tones)
    ycrcb = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2YCrCb)
    # Typical skin range in YCrCb: Cr in [133, 173], Cb in [77, 127]
    lower_ycrcb = np.array([0, 133, 77], dtype=np.uint8)
    upper_ycrcb = np.array([255, 175, 127], dtype=np.uint8)
    mask_ycrcb = cv2.inRange(ycrcb, lower_ycrcb, upper_ycrcb)

    # 2. HSV check for additional skin tone confirmation
    hsv = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2HSV)
    lower_hsv = np.array([0, 20, 50], dtype=np.uint8)
    upper_hsv = np.array([25, 255, 255], dtype=np.uint8)
    mask_hsv = cv2.inRange(hsv, lower_hsv, upper_hsv)

    skin_mask = cv2.bitwise_and(mask_ycrcb, mask_hsv)

    # Slight dilation to protect delicate facial margins & ears
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    protected_skin = cv2.dilate(skin_mask, kernel, iterations=1)
    return protected_skin


def segment_chroma_key(
    rgb_img: np.ndarray,
    target_color_rgb: Tuple[int, int, int],
    tolerance: float = 0.28,
    softness: float = 0.12,
    protect_skin: bool = True
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Performs HSV hue+saturation based chroma segmentation.
    HSV-space keying is much more reliable than RGB Euclidean distance for
    green/blue screens because it separates color (hue) from brightness (value),
    avoiding the common problem where bright or shadowed areas of the backdrop
    fail to be removed.

    Returns:
    - raw_mask: 2D uint8 (0 = background, 255 = foreground)
    - despilled_rgb: RGB image with background color spill neutralized on hair/edges
    """
    h, w = rgb_img.shape[:2]

    # Convert to HSV for hue-based keying
    hsv_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2HSV).astype(np.float32)
    h_ch = hsv_img[:, :, 0]   # Hue: 0-180 in OpenCV
    s_ch = hsv_img[:, :, 1]   # Saturation: 0-255
    v_ch = hsv_img[:, :, 2]   # Value: 0-255

    # Convert target color to HSV
    target_px = np.uint8([[list(target_color_rgb)]])
    target_hsv = cv2.cvtColor(target_px, cv2.COLOR_RGB2HSV)[0, 0].astype(np.float32)
    t_hue = float(target_hsv[0])
    t_sat = float(target_hsv[1])
    t_val = float(target_hsv[2])

    # Determine if chroma keying makes sense (green or blue screen)
    t_r, t_g, t_b = target_color_rgb
    is_green = (t_g > t_r and t_g > t_b)
    is_blue  = (t_b > t_r and t_b > t_g)

    if is_green or is_blue:
        # --- HSV hue-based keying (best for colored backdrops) ---
        # Hue distance (circular, wrapped at 180)
        hue_diff = np.abs(h_ch - t_hue)
        hue_diff = np.minimum(hue_diff, 180.0 - hue_diff)  # Wrap-around

        # Saturation distance normalized to 0-1
        sat_diff = np.abs(s_ch - t_sat) / 255.0

        # Combined weighted distance: hue matters most, saturation helps
        # Hue tolerance: ~30° maps to ~0 alpha (background), >60° -> foreground
        hue_tol_low  = 25.0   # degrees: definitely background
        hue_tol_high = 55.0   # degrees: transition zone ends

        hue_alpha = np.clip((hue_diff - hue_tol_low) / (hue_tol_high - hue_tol_low), 0.0, 1.0)

        # Low-saturation pixels are likely desaturated subject pixels (e.g. grey shirt) — keep them
        # High-saturation pixels matching target hue are definitely background
        sat_factor = np.clip(s_ch / 255.0, 0.0, 1.0)  # 0=grey -> keep, 1=vivid -> key it
        # When saturation is very low (<0.15), override: keep as foreground regardless of hue
        low_sat_override = (s_ch < 38).astype(np.float32)  # 38/255 ≈ 15%

        alpha_float = hue_alpha + (1.0 - hue_alpha) * (1.0 - sat_factor)
        alpha_float = np.clip(alpha_float, 0.0, 1.0)
        alpha_float = np.maximum(alpha_float, low_sat_override)

    else:
        # --- RGB Euclidean fallback for non-standard backdrop colors ---
        img_float = rgb_img.astype(np.float32) / 255.0
        target_float = np.array(target_color_rgb, dtype=np.float32) / 255.0
        diff = img_float - target_float
        color_dist = np.sqrt(np.sum(diff * diff, axis=-1))
        t_low  = tolerance
        t_high = tolerance + max(softness, 0.01)
        alpha_float = np.clip((color_dist - t_low) / (t_high - t_low), 0.0, 1.0)

    raw_mask = (alpha_float * 255.0).astype(np.uint8)

    # Protect person's face, ears, and neck from accidental chroma match
    if protect_skin:
        skin = create_skin_protection_mask(rgb_img)
        # Never allow skin pixels to be classified as background
        raw_mask = np.maximum(raw_mask, skin)

    # Morphological cleanup: fill any isolated green holes inside subject silhouette
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    raw_mask = cv2.morphologyEx(raw_mask, cv2.MORPH_CLOSE, kernel_close)

    # Despill: suppress target backdrop hue on border fringes
    despilled_rgb = suppress_chroma_spill(rgb_img, raw_mask, target_color_rgb)

    return raw_mask, despilled_rgb


def suppress_chroma_spill(
    rgb_img: np.ndarray,
    mask: np.ndarray,
    target_color_rgb: Tuple[int, int, int]
) -> np.ndarray:
    """
    Neutralizes green or blue screen bounce light reflected on the hair, shoulders, and clothes.
    """
    # Detect fringe zone: morphological boundary of subject (inner ~5px) plus soft alpha transition
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    fg_binary = (mask > 50).astype(np.uint8)
    eroded_fg = cv2.erode(fg_binary, kernel, iterations=1)
    fringe_zone = (fg_binary == 1) & (eroded_fg == 0)
    transition_zone = fringe_zone | ((mask > 5) & (mask < 245))

    if not np.any(transition_zone):
        return rgb_img

    result = rgb_img.copy()

    # Determine dominant spill channel
    t_r, t_g, t_b = target_color_rgb
    is_green = (t_g > t_r and t_g > t_b)
    is_blue = (t_b > t_r and t_b > t_g)

    r = result[:, :, 0].astype(np.float32)
    g = result[:, :, 1].astype(np.float32)
    b = result[:, :, 2].astype(np.float32)

    if is_green:
        # Green despill: on subject boundary, clamp green if it dominates red and blue
        excess_g = transition_zone & (g > r) & (g > b)
        max_allowed_g = (r + b) * 0.5
        g[excess_g] = np.minimum(g[excess_g], max_allowed_g[excess_g])
        result[:, :, 1] = np.clip(g, 0, 255).astype(np.uint8)
    elif is_blue:
        # Blue despill: on subject boundary, clamp blue if it dominates red and green
        excess_b = transition_zone & (b > r) & (b > g)
        max_allowed_b = (r + g) * 0.5
        b[excess_b] = np.minimum(b[excess_b], max_allowed_b[excess_b])
        result[:, :, 2] = np.clip(b, 0, 255).astype(np.uint8)
    else:
        # General despill: desaturate boundary in HSV
        hsv = cv2.cvtColor(result, cv2.COLOR_RGB2HSV).astype(np.float32)
        h, s, v = cv2.split(hsv)
        s[transition_zone] = s[transition_zone] * 0.4
        hsv_clean = cv2.merge([h, s, v]).astype(np.uint8)
        result[transition_zone] = cv2.cvtColor(hsv_clean, cv2.COLOR_HSV2RGB)[transition_zone]

    return result
