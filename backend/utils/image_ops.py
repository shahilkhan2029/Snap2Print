from pathlib import Path
from typing import Tuple
from PIL import Image, ImageOps
import io

from backend.config import ALLOWED_EXTENSIONS, MAX_DIMENSION, MAX_FILE_SIZE_MB


def validate_image_file(filename: str, file_size: int) -> None:
    """Validates file extension and size limits."""
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file format '{suffix}'. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise ValueError(
            f"File is too large ({file_size / (1024 * 1024):.1f} MB). Maximum allowed size is {MAX_FILE_SIZE_MB} MB."
        )


def load_and_preprocess_image(image_bytes: bytes) -> Tuple[Image.Image, Tuple[int, int]]:
    """
    Safely opens an image from bytes, verifies integrity, applies EXIF orientation
    (fixes camera rotation for DSLR/phone photos), converts to RGB,
    and returns (image, original_size).
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.load()  # Force reading all pixels to detect truncated/corrupted files
    except Exception as e:
        raise ValueError(f"Corrupted or invalid image file: {str(e)}")

    # Apply EXIF orientation so DSLR/phone photos are not rotated incorrectly.
    # This fixes the classic "image appears 90° rotated" bug with JPEG camera files.
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass  # Non-JPEG or no EXIF — safe to ignore

    original_size = img.size  # (width, height) — after orientation correction

    # Convert grayscale, indexed, CMYK, or RGBA to clean RGB
    if img.mode != "RGB":
        img = img.convert("RGB")

    return img, original_size


def resize_if_needed(image: Image.Image, max_dim: int = MAX_DIMENSION) -> Tuple[Image.Image, bool]:
    """
    Prevents CPU choking on gigantic raw camera photos by downsizing proportionally
    for AI segmentation, while tracking if resizing occurred.
    """
    w, h = image.size
    if max(w, h) > max_dim:
        scale = max_dim / float(max(w, h))
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        return resized, True
    return image, False
