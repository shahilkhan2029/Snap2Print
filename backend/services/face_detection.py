"""
Face Detection Service for Snap2Print (Task 1).

Model: YuNet (OpenCV Zoo)
License: Apache 2.0 (Lightweight, commercial-friendly)
Model Size: ~232 KB (ONNX)
Inference Engine: OpenCV DNN FaceDetectorYN (CPU optimized)
Speed: ~10-25 ms on Intel i5 CPU
Capabilities:
- Primary face detection (bounding box: x, y, width, height)
- 5 facial keypoints / landmarks:
    * Right eye
    * Left eye
    * Nose tip
    * Right mouth corner
    * Left mouth corner
- Confidence score (0.0 to 1.0)
- Normalized coordinates (0.0 to 1.0) for resolution-independent overlay rendering
"""
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union, List
import cv2
import numpy as np
from PIL import Image

from backend.config import MODELS_DIR

logger = logging.getLogger(__name__)

YUNET_MODEL_FILENAME = "face_detection_yunet.onnx"
YUNET_MODEL_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"


class FaceDetectionService:
    """
    Singleton Face Detection service powered by OpenCV's YuNet ONNX model.
    Loaded once and kept in memory for zero repeated overhead.
    """

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path or (MODELS_DIR / YUNET_MODEL_FILENAME)
        self.detector = None
        self._ensure_model_file()
        self._initialize()

    def _ensure_model_file(self):
        """Ensures the YuNet ONNX model exists on disk, downloading if missing."""
        if not self.model_path.exists():
            import urllib.request
            logger.info(f"Downloading YuNet face detection model to {self.model_path}...")
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(YUNET_MODEL_URL, self.model_path)
            logger.info("YuNet model download complete.")

    def _initialize(self):
        try:
            logger.info(f"Initializing FaceDetectorYN with model: {self.model_path.name}...")
            t0 = time.time()
            # Initialize with default placeholder size; dynamically updated per image
            self.detector = cv2.FaceDetectorYN.create(
                model=str(self.model_path),
                config="",
                input_size=(320, 320),
                score_threshold=0.35,
                nms_threshold=0.3,
                top_k=5000
            )
            load_ms = int((time.time() - t0) * 1000)
            logger.info(f"FaceDetectorYN initialized successfully in {load_ms} ms.")
        except Exception as e:
            logger.error(f"Failed to initialize FaceDetectorYN: {e}", exc_info=True)
            self.detector = None
            raise RuntimeError(f"Face detector initialization error: {e}")

    def detect_primary_face(
        self,
        image: Union[Image.Image, np.ndarray],
        original_size: Optional[Tuple[int, int]] = None
    ) -> Dict[str, Any]:
        """
        Detects the primary human face in the given image.

        Args:
            image: PIL Image or numpy RGB/BGR array
            original_size: (width, height) of full-resolution original image for mapping

        Returns:
            Dictionary containing:
            - detected: bool
            - status: str ("Face detected" or "No face detected")
            - confidence: float (0.0 to 1.0)
            - bounding_box: dict with pixel (x, y, width, height) & normalized (0..1)
            - landmarks: dict with 5 keypoint coordinates (pixel & normalized)
            - face_count: int (total faces detected in image)
            - inference_time_ms: int
        """
        if self.detector is None:
            self._initialize()

        t0 = time.time()

        # Convert input to BGR numpy array
        if isinstance(image, Image.Image):
            rgb_np = np.array(image.convert("RGB"))
            bgr_np = cv2.cvtColor(rgb_np, cv2.COLOR_RGB2BGR)
            img_w, img_h = image.size
        elif isinstance(image, np.ndarray):
            if image.shape[2] == 4:
                # RGBA -> BGR
                bgr_np = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
            elif image.shape[2] == 3:
                # Assume RGB -> BGR
                bgr_np = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            else:
                bgr_np = image
            img_h, img_w = bgr_np.shape[:2]
        else:
            raise ValueError("Unsupported image type for face detection.")

        orig_w = original_size[0] if original_size else img_w
        orig_h = original_size[1] if original_size else img_h

        # Downscale for ultra-fast CPU inference if image is excessively large (keeps latency <25ms)
        max_det_dim = 1200
        scale_det = 1.0
        if max(img_w, img_h) > max_det_dim:
            scale_det = max_det_dim / float(max(img_w, img_h))
            inf_w = max(int(img_w * scale_det), 32)
            inf_h = max(int(img_h * scale_det), 32)
            bgr_for_det = cv2.resize(bgr_np, (inf_w, inf_h), interpolation=cv2.INTER_LINEAR)
        else:
            bgr_for_det = bgr_np
            inf_w, inf_h = img_w, img_h

        # Update input size for detector
        self.detector.setInputSize((inf_w, inf_h))

        # Run inference
        _, faces = self.detector.detect(bgr_for_det)
        elapsed_ms = int((time.time() - t0) * 1000)

        if faces is None or len(faces) == 0:
            return {
                "detected": False,
                "status": "No face detected",
                "confidence": 0.0,
                "bounding_box": None,
                "landmarks": None,
                "face_count": 0,
                "inference_time_ms": elapsed_ms
            }

        # Process all detected faces
        faces_data = []
        inv_scale = 1.0 / scale_det
        scale_x = orig_w / float(img_w)
        scale_y = orig_h / float(img_h)

        # Sort faces from left to right for intuitive numbering
        sorted_faces = sorted(faces, key=lambda f: float(f[0]))

        for idx, f in enumerate(sorted_faces, start=1):
            bx = max(0, int(f[0] * inv_scale))
            by = max(0, int(f[1] * inv_scale))
            bw = min(int(f[2] * inv_scale), img_w - bx)
            bh = min(int(f[3] * inv_scale), img_h - by)
            conf = round(float(f[14]), 3)

            lm_raw = [float(v) * inv_scale for v in f[4:14]]
            landmarks_data = {
                "right_eye": {
                    "x": int(lm_raw[0]), "y": int(lm_raw[1]),
                    "x_norm": round(lm_raw[0] / float(img_w), 4), "y_norm": round(lm_raw[1] / float(img_h), 4),
                    "orig_x": int(lm_raw[0] * scale_x), "orig_y": int(lm_raw[1] * scale_y)
                },
                "left_eye": {
                    "x": int(lm_raw[2]), "y": int(lm_raw[3]),
                    "x_norm": round(lm_raw[2] / float(img_w), 4), "y_norm": round(lm_raw[3] / float(img_h), 4),
                    "orig_x": int(lm_raw[2] * scale_x), "orig_y": int(lm_raw[3] * scale_y)
                },
                "nose_tip": {
                    "x": int(lm_raw[4]), "y": int(lm_raw[5]),
                    "x_norm": round(lm_raw[4] / float(img_w), 4), "y_norm": round(lm_raw[5] / float(img_h), 4),
                    "orig_x": int(lm_raw[4] * scale_x), "orig_y": int(lm_raw[5] * scale_y)
                },
                "right_mouth": {
                    "x": int(lm_raw[6]), "y": int(lm_raw[7]),
                    "x_norm": round(lm_raw[6] / float(img_w), 4), "y_norm": round(lm_raw[7] / float(img_h), 4),
                    "orig_x": int(lm_raw[6] * scale_x), "orig_y": int(lm_raw[7] * scale_y)
                },
                "left_mouth": {
                    "x": int(lm_raw[8]), "y": int(lm_raw[9]),
                    "x_norm": round(lm_raw[8] / float(img_w), 4), "y_norm": round(lm_raw[9] / float(img_h), 4),
                    "orig_x": int(lm_raw[8] * scale_x), "orig_y": int(lm_raw[9] * scale_y)
                }
            }

            bbox_data = {
                "x": bx,
                "y": by,
                "width": bw,
                "height": bh,
                "orig_x": int(bx * scale_x),
                "orig_y": int(by * scale_y),
                "orig_width": int(bw * scale_x),
                "orig_height": int(bh * scale_y),
                "x_norm": round(bx / float(img_w), 4),
                "y_norm": round(by / float(img_h), 4),
                "w_norm": round(bw / float(img_w), 4),
                "h_norm": round(bh / float(img_h), 4)
            }

            faces_data.append({
                "id": idx,
                "label": f"Face {idx}",
                "confidence": conf,
                "bounding_box": bbox_data,
                "landmarks": landmarks_data
            })

        count = len(faces_data)
        if count == 0:
            return {
                "detected": False,
                "status": "No face detected",
                "confidence": 0.0,
                "bounding_box": None,
                "landmarks": None,
                "face_count": 0,
                "faces": [],
                "inference_time_ms": elapsed_ms
            }

        # Identify most prominent / largest face as primary face
        primary_face = max(faces_data, key=lambda f: f["bounding_box"]["width"] * f["bounding_box"]["height"])
        status_text = f"{count} faces detected" if count > 1 else "Face detected"

        logger.debug(f"{count} face(s) detected in {elapsed_ms}ms")

        return {
            "detected": True,
            "status": status_text,
            "face_count": count,
            "confidence": primary_face["confidence"],
            "bounding_box": primary_face["bounding_box"],
            "landmarks": primary_face["landmarks"],
            "primary_face": primary_face,
            "faces": faces_data,
            "inference_time_ms": elapsed_ms
        }


# Global singleton instance
_face_detector_instance: Optional[FaceDetectionService] = None


def get_face_detector() -> FaceDetectionService:
    global _face_detector_instance
    if _face_detector_instance is None:
        _face_detector_instance = FaceDetectionService()
    return _face_detector_instance
