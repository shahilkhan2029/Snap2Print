"""
Passport Photo Auto-Crop Service for Snap2Print.

Computes framing for passport and ID photos based on facial detection
landmarks and international standards (ICAO Doc 9303).

Standards:
- Standard Passport: 35mm x 45mm (Aspect ratio 7:9 ~ 0.7778)
- US Passport: 2 x 2 inch (Aspect ratio 1:1)
- Standard ID / Visa: 30mm x 40mm (Aspect ratio 3:4 = 0.75)

Framing Rules:
- Head height (crown/hair to chin) occupies ~70-75% of vertical frame height.
- Eye level is positioned ~58-62% from bottom (~38-42% from top).
- Midline between eyes is centered horizontally.
- Neck and top of shoulders are preserved without clipping.
- Boundaries are constrained to the parent image while preserving aspect ratio.
"""
from typing import Dict, Any, Tuple, Optional


ASPECT_RATIOS = {
    "35:45": 35.0 / 45.0,  # Standard International Passport (7:9 ~ 0.7778)
    "1:1": 1.0,            # US Passport (2x2 inch)
    "3:4": 3.0 / 4.0,      # Standard Portrait / Visa
}


def calculate_passport_crop(
    face: Dict[str, Any],
    image_width: int,
    image_height: int,
    aspect_ratio_name: str = "35:45"
) -> Dict[str, Any]:
    """
    Calculates passport photo crop bounding box for a specific face.

    Args:
        face: Face dictionary containing 'bounding_box' and 'landmarks'
        image_width: Full image width in pixels
        image_height: Full image height in pixels
        aspect_ratio_name: Key in ASPECT_RATIOS (default "35:45")

    Returns:
        Dictionary with pixel crop (x, y, width, height) and normalized (0..1)
    """
    ratio = ASPECT_RATIOS.get(aspect_ratio_name, 35.0 / 45.0)

    bbox = face.get("bounding_box", {})
    face_x = bbox.get("orig_x", bbox.get("x", 0))
    face_y = bbox.get("orig_y", bbox.get("y", 0))
    face_w = bbox.get("orig_width", bbox.get("width", 100))
    face_h = bbox.get("orig_height", bbox.get("height", 100))

    landmarks = face.get("landmarks", {})
    if landmarks and "right_eye" in landmarks and "left_eye" in landmarks:
        re = landmarks["right_eye"]
        le = landmarks["left_eye"]
        re_x = re.get("orig_x", re.get("x", face_x + face_w * 0.3))
        re_y = re.get("orig_y", re.get("y", face_y + face_h * 0.35))
        le_x = le.get("orig_x", le.get("x", face_x + face_w * 0.7))
        le_y = le.get("orig_y", le.get("y", face_y + face_h * 0.35))

        center_eye_x = (re_x + le_x) / 2.0
        center_eye_y = (re_y + le_y) / 2.0
    else:
        center_eye_x = face_x + face_w / 2.0
        center_eye_y = face_y + face_h * 0.38

    # Head height in passport: Face box is ~48% of total crop height to include hair and shoulders
    target_crop_h = int(face_h * 2.2)

    # Calculate width based on requested aspect ratio
    target_crop_w = int(target_crop_h * ratio)

    # Check that crop doesn't exceed image dimensions
    if target_crop_h > image_height:
        target_crop_h = image_height
        target_crop_w = int(target_crop_h * ratio)
    if target_crop_w > image_width:
        target_crop_w = image_width
        target_crop_h = int(target_crop_w / ratio)

    # Vertical position: Eye line at 40% from top of crop
    crop_y = int(center_eye_y - (target_crop_h * 0.40))
    # Horizontal position: Center eye midpoint centered in crop
    crop_x = int(center_eye_x - (target_crop_w / 2.0))

    # Boundary safety checks and shifting
    if crop_x < 0:
        crop_x = 0
    elif crop_x + target_crop_w > image_width:
        crop_x = max(0, image_width - target_crop_w)

    if crop_y < 0:
        crop_y = 0
    elif crop_y + target_crop_h > image_height:
        crop_y = max(0, image_height - target_crop_h)

    # Re-verify boundaries
    final_w = min(target_crop_w, image_width - crop_x)
    final_h = min(target_crop_h, image_height - crop_y)

    return {
        "x": int(crop_x),
        "y": int(crop_y),
        "width": int(final_w),
        "height": int(final_h),
        "aspect_ratio": aspect_ratio_name,
        "ratio_val": round(final_w / float(final_h) if final_h > 0 else 1.0, 4),
        "x_norm": round(crop_x / float(image_width), 4),
        "y_norm": round(crop_y / float(image_height), 4),
        "w_norm": round(final_w / float(image_width), 4),
        "h_norm": round(final_h / float(image_height), 4)
    }


def calculate_default_center_crop(
    image_width: int,
    image_height: int,
    aspect_ratio_name: str = "35:45"
) -> Dict[str, Any]:
    """
    Calculates a sensible centered passport crop rectangle when no face is detected,
    allowing the user to manually reposition and scale it.
    """
    ratio = ASPECT_RATIOS.get(aspect_ratio_name, 35.0 / 45.0)
    target_crop_h = int(image_height * 0.72)
    target_crop_w = int(target_crop_h * ratio)
    if target_crop_w > image_width:
        target_crop_w = int(image_width * 0.85)
        target_crop_h = int(target_crop_w / ratio)

    crop_x = max(0, int((image_width - target_crop_w) / 2))
    crop_y = max(0, int((image_height - target_crop_h) * 0.35))

    return {
        "x": int(crop_x),
        "y": int(crop_y),
        "width": int(target_crop_w),
        "height": int(target_crop_h),
        "aspect_ratio": aspect_ratio_name,
        "ratio_val": round(target_crop_w / float(target_crop_h) if target_crop_h > 0 else 1.0, 4),
        "x_norm": round(crop_x / float(image_width), 4),
        "y_norm": round(crop_y / float(image_height), 4),
        "w_norm": round(target_crop_w / float(image_width), 4),
        "h_norm": round(target_crop_h / float(image_height), 4)
    }

