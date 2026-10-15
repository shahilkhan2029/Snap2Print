"""
MediaPipe Selfie Segmentation service — Ultra-Fast CPU Portrait Segmentation.

Model: MediaPipe Selfie Segmenter (Google TFLite / XNNPACK)
License: Apache 2.0 (Free for commercial and personal use)
Inference Engine: TensorFlow Lite XNNPACK Delegate (CPU optimized)
Speed: ~10-40 ms on CPU (2,000x faster than BiRefNet)
Quality: Excellent for studio portraits, passports, and casual photos.

BiRefNet is retained as 'Studio Quality' on-demand option for complex hair matting.
"""
import logging
import time
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import numpy as np
from PIL import Image

from backend.config import MODELS_DIR

logger = logging.getLogger(__name__)

MODEL_FILENAME = "selfie_segmenter.tflite"
MODEL_DOWNLOAD_URL = "https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_segmenter/float16/latest/selfie_segmenter.tflite"


class MediaPipeSegmentationBackend:
    """
    MediaPipe Selfie Segmentation singleton using Tasks API.
    Loaded once on startup and reused across all requests.
    Runs on CPU with TensorFlow Lite XNNPACK acceleration (~10-40ms).
    """

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path or (MODELS_DIR / MODEL_FILENAME)
        self._segmenter = None
        self._ensure_model_file()
        self._initialize()

    def _ensure_model_file(self):
        """Ensures the TFLite model file is available on disk, downloading if necessary."""
        if not self.model_path.exists():
            import urllib.request
            logger.info(f"Downloading MediaPipe model to {self.model_path}...")
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(MODEL_DOWNLOAD_URL, self.model_path)
            logger.info("MediaPipe model download complete.")

    def _initialize(self):
        try:
            import mediapipe as mp
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision

            logger.info(f"Initializing MediaPipe ImageSegmenter ({self.model_path.name})...")
            t0 = time.time()
            base_options = python.BaseOptions(model_asset_path=str(self.model_path))
            options = vision.ImageSegmenterOptions(
                base_options=base_options,
                output_category_mask=False,
                output_confidence_masks=True
            )
            self._segmenter = vision.ImageSegmenter.create_from_options(options)
            load_ms = int((time.time() - t0) * 1000)
            logger.info(f"MediaPipe Selfie Segmenter ready in {load_ms} ms.")
        except Exception as e:
            logger.error(f"MediaPipe initialization failed: {e}", exc_info=True)
            raise RuntimeError(f"MediaPipe initialization error: {e}")

    def segment_mask(
        self,
        image: Image.Image,
        seg_resolution: int = 1024
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Segments the subject from a PIL RGB image.

        Returns:
        - raw_mask: 2D uint8 ndarray (0=background, 255=foreground) matching original image dimensions
        - metadata: dict with timing and model details
        """
        import cv2
        import mediapipe as mp

        # Step 1: Ensure image is 3-channel RGB (MediaPipe SRGB requires exactly 3 channels: R, G, B)
        rgb_image = image.convert("RGB") if image.mode != "RGB" else image

        orig_w, orig_h = rgb_image.size
        t0 = time.time()

        # Step 2: Scale if image is excessively large to keep inference sub-50ms
        scale = min(seg_resolution / max(orig_w, orig_h), 1.0)
        inf_w = max(int(orig_w * scale), 32)
        inf_h = max(int(orig_h * scale), 32)
        if (inf_w, inf_h) != (orig_w, orig_h):
            img_for_inf = rgb_image.resize((inf_w, inf_h), Image.Resampling.BILINEAR)
        else:
            img_for_inf = rgb_image

        rgb_np = np.array(img_for_inf, dtype=np.uint8)
        if rgb_np.ndim == 2:
            rgb_np = np.stack([rgb_np] * 3, axis=-1)
        elif rgb_np.ndim == 3 and rgb_np.shape[2] == 4:
            rgb_np = rgb_np[:, :, :3]

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_np)

        # Step 2: Run inference
        result = self._segmenter.segment(mp_image)
        confidence_mask = result.confidence_masks[0].numpy_view()
        if confidence_mask.ndim == 3:
            confidence_mask = confidence_mask[:, :, 0]

        # Step 3: Upscale confidence mask back to original resolution if needed
        if confidence_mask.shape != (orig_h, orig_w):
            mask_upscaled = cv2.resize(
                confidence_mask,
                (orig_w, orig_h),
                interpolation=cv2.INTER_LANCZOS4
            )
        else:
            mask_upscaled = confidence_mask

        # Step 4: Alpha thresholding with feathered edges
        threshold_hard = 0.65
        threshold_soft = 0.25
        alpha = np.clip(
            (mask_upscaled - threshold_soft) / (threshold_hard - threshold_soft),
            0.0, 1.0
        )
        raw_mask = (alpha * 255.0).astype(np.uint8)

        inference_ms = int((time.time() - t0) * 1000)
        logger.debug(f"MediaPipe segmentation: {orig_w}x{orig_h} in {inference_ms}ms")

        metadata = {
            "model_name": "MediaPipe Selfie Segmenter",
            "license": "Apache 2.0",
            "inference_resolution": f"{inf_w}x{inf_h}",
            "output_resolution": f"{orig_w}x{orig_h}",
            "inference_time_ms": inference_ms
        }
        return raw_mask, metadata

    def close(self):
        """Releases underlying model resources."""
        if self._segmenter:
            try:
                self._segmenter.close()
            except Exception:
                pass
            self._segmenter = None


# Global singleton instance
_mediapipe_instance: Optional[MediaPipeSegmentationBackend] = None


def get_mediapipe_segmentor() -> MediaPipeSegmentationBackend:
    global _mediapipe_instance
    if _mediapipe_instance is None:
        _mediapipe_instance = MediaPipeSegmentationBackend()
    return _mediapipe_instance
