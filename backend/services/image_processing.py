"""
Image processing utilities for compositing, format conversion, and color manipulation.
Designed for performance, avoiding redundant memory copies.
"""
from typing import Optional, Tuple
from PIL import Image
import numpy as np


def apply_alpha_to_image(rgb_image: Image.Image, alpha_mask: np.ndarray) -> Image.Image:
    """Combines an RGB PIL image with a 2D numpy uint8 alpha mask into RGBA."""
    r, g, b = rgb_image.split()
    alpha_pil = Image.fromarray(alpha_mask, mode="L")
    return Image.merge("RGBA", (r, g, b, alpha_pil))


def composite_on_background(
    rgba_image: Image.Image,
    bg_type: str = "transparent",
    custom_hex: Optional[str] = None
) -> Image.Image:
    """
    Renders the foreground RGBA onto a selected studio background.
    - 'transparent': Direct RGBA PNG
    - 'white': #FFFFFF (Passport standard pure white)
    - 'blue': #1877F2 (Standard studio passport blue)
    - 'custom': Hex color code
    """
    if bg_type == "transparent":
        return rgba_image

    width, height = rgba_image.size

    color_rgb = (255, 255, 255)
    if bg_type == "white":
        color_rgb = (255, 255, 255)
    elif bg_type == "blue":
        color_rgb = (24, 119, 242)
    elif bg_type == "custom" and custom_hex:
        clean_hex = custom_hex.lstrip("#")
        if len(clean_hex) == 6:
            try:
                color_rgb = tuple(int(clean_hex[i : i + 2], 16) for i in (0, 2, 4))
            except ValueError:
                color_rgb = (255, 255, 255)

    background = Image.new("RGBA", (width, height), (*color_rgb, 255))
    return Image.alpha_composite(background, rgba_image)
