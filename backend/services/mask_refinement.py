"""
Controlled mask refinement service.
Operates on raw masks from either Chroma Key or U2NetP:
1. Removes tiny isolated background components.
2. Fills small internal gaps / clothing holes.
3. Applies controlled morphological closing.
4. Softens jagged pixel boundaries without blurring or cutting shoulders/ears/hair.
5. Keeps the person's true silhouette intact.
"""
import cv2
import numpy as np
from typing import Tuple, Dict, Any


def refine_hybrid_mask(
    raw_mask: np.ndarray,
    guide_img: np.ndarray,
    smoothness: float = 1.0,
    min_component_ratio: float = 0.002,
    max_hole_ratio: float = 0.05
) -> np.ndarray:
    """
    Refines raw mask cleanly without aggressive blur or erosion.
    """
    h, w = raw_mask.shape[:2]
    total_area = h * w
    mask = raw_mask.copy()

    # 1. Fill small holes inside the subject (clothing, hair, suit)
    # Binary representation of background
    binary = (mask > 120).astype(np.uint8) * 255
    inverted = cv2.bitwise_not(binary)
    contours, hierarchy = cv2.findContours(inverted, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    max_hole_px = int(total_area * max_hole_ratio)
    if hierarchy is not None:
        for idx, cnt in enumerate(contours):
            # Check if this contour is an interior hole enclosed by foreground
            if hierarchy[0][idx][3] != -1:
                if cv2.contourArea(cnt) <= max_hole_px:
                    cv2.drawContours(mask, [cnt], -1, 255, -1)

    # 2. Filter tiny detached noise fragments outside the person
    bin_fg = (mask > 70).astype(np.uint8)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(bin_fg, connectivity=8)
    min_comp_px = int(total_area * min_component_ratio)

    if num_labels > 2:
        # Keep background (label 0) and largest components
        for label in range(1, num_labels):
            area = stats[label, cv2.CC_STAT_AREA]
            if area < min_comp_px:
                mask[labels == label] = 0

    # 3. Controlled morphological closing (heals hairline fractures without shrinking borders)
    k_size = 3 if smoothness <= 1.2 else 5
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_size, k_size))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 4. Controlled edge transition (feather without destroying silhouette)
    # Define narrow boundary band
    dilated = cv2.dilate(mask, kernel, iterations=1)
    eroded = cv2.erode(mask, kernel, iterations=1)
    boundary_band = cv2.subtract(dilated, eroded)

    # Edge-preserving bilateral filter on mask
    soft_edge = cv2.bilateralFilter(mask, d=5, sigmaColor=50, sigmaSpace=50)

    # Blend: inside solid core remains full 255, outside remains 0, boundary uses soft transition
    refined = np.where(eroded > 240, mask, soft_edge)
    refined = np.where(dilated < 15, 0, refined)

    # Subtle 3x3 Gaussian smoothing specifically on the narrow boundary band
    refined_f = refined.astype(np.float32) / 255.0
    feathered = cv2.GaussianBlur(refined_f, (3, 3), 0.5)

    final_alpha = np.where(boundary_band > 0, feathered, refined_f)
    return np.clip(final_alpha * 255.0, 0, 255).astype(np.uint8)


def evaluate_mask_quality(mask: np.ndarray) -> Dict[str, Any]:
    """
    Evaluates quality without claiming official government standard.
    """
    h, w = mask.shape[:2]
    total_pixels = h * w
    fg_pixels = np.count_nonzero(mask > 120)
    fg_ratio = fg_pixels / float(total_pixels)

    issues = []
    if fg_ratio < 0.05:
        issues.append("Subject appears missing or cropped out.")
        return {"status": "Poor", "grade": "Poor", "reason": "Subject area too small", "issues": issues}
    if fg_ratio > 0.95:
        issues.append("Background was barely detected/removed.")
        return {"status": "Poor", "grade": "Poor", "reason": "Almost entire image selected", "issues": issues}

    # Floating fragments check
    binary = (mask > 80).astype(np.uint8)
    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    small_fragments = 0
    min_noise = int(total_pixels * 0.0005)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] < min_noise:
            small_fragments += 1

    if small_fragments > 40:
        issues.append(f"Detected {small_fragments} small background artifacts.")

    if len(issues) == 0:
        return {"status": "Good", "grade": "Good", "reason": "Clean borders and solid subject detected", "issues": []}
    else:
        return {"status": "Needs Review", "grade": "Needs Review", "reason": "; ".join(issues), "issues": issues}
