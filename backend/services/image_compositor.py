"""
Image compositor service.
Composites foreground subject behind requested studio backgrounds:
- Transparent (RGBA PNG)
- Studio White (#FFFFFF)
- Passport Blue (#1877F2 or standard #1E6091)
- Custom studio color

Preserves 100% of original person's pixels without degradation.
"""
from typing import Optional, Tuple
from PIL import Image
import numpy as np


def apply_mask_to_foreground(rgb_img: Image.Image, alpha_mask: np.ndarray) -> Image.Image:
    """Takes an RGB PIL Image and uint8 alpha mask, merges into RGBA."""
    r, g, b = rgb_img.split()
    alpha_pil = Image.fromarray(alpha_mask, mode="L")
    return Image.merge("RGBA", (r, g, b, alpha_pil))


def composite_studio_background(
    rgba_image: Image.Image,
    bg_type: str = "transparent",
    custom_hex: Optional[str] = None
) -> Image.Image:
    """
    Renders clean background behind the person.
    """
    if bg_type == "transparent":
        return rgba_image

    width, height = rgba_image.size
    color_rgb = (255, 255, 255)

    if bg_type == "white":
        color_rgb = (255, 255, 255)
    elif bg_type == "blue":
        color_rgb = (24, 119, 242) # Standard studio passport blue
    elif bg_type == "custom" and custom_hex:
        clean_hex = custom_hex.lstrip("#")
        if len(clean_hex) == 6:
            try:
                color_rgb = tuple(int(clean_hex[i : i + 2], 16) for i in (0, 2, 4))
            except ValueError:
                color_rgb = (255, 255, 255)

    background = Image.new("RGBA", (width, height), (*color_rgb, 255))
    return Image.alpha_composite(background, rgba_image)
