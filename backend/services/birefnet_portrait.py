"""
BiRefNet-Portrait background segmentation service.

Model: BiRefNet-portrait-epoch_150 (ZhengPeng7/BiRefNet)
License: MIT License (Commercial and closed-source friendly)
Inference Engine: ONNX Runtime (CPU prioritized, CUDA autodetection)
Input Resolution: 1024x1024 normalized tensor
Inference Mode: No-gradient inference, persistent singleton session
"""
import os
import time
import logging
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any, Optional
from PIL import Image
import numpy as np

from backend.config import MODELS_DIR, get_model_file

logger = logging.getLogger(__name__)

# Target standard inference dimension for BiRefNet
BIREFNET_INFERENCE_SIZE = (1024, 1024)


class BiRefNetPortraitBackend:
    """
    BiRefNet Portrait model session singleton.
    Loaded once and kept in-memory for zero repeated loading overhead.
    """

    def __init__(self, model_name: str = "birefnet-portrait"):
        self.model_name = model_name
        self.session = None
        self._initialize_session()

    def _initialize_session(self):
        try:
            biref_path = get_model_file(f"models/{self.model_name}/{self.model_name}.onnx")
            if biref_path.exists():
                os.environ["U2NET_HOME"] = str(biref_path.parent.parent.parent)
            else:
                os.environ["U2NET_HOME"] = str(MODELS_DIR)
            import rembg
            import onnxruntime as ort
            sess_opts = ort.SessionOptions()
            cpu_count = min(os.cpu_count() or 4, 4)
            sess_opts.intra_op_num_threads = cpu_count
            sess_opts.inter_op_num_threads = 1
            sess_opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            sess_opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

            logger.info(f"Initializing persistent BiRefNet-Portrait session (threads={cpu_count})...")
            t0 = time.time()
            self.session = rembg.new_session(self.model_name, sess_opts=sess_opts)
            load_time = int((time.time() - t0) * 1000)
            logger.info(f"BiRefNet-Portrait session initialized successfully in {load_time} ms.")
        except Exception as e:
            logger.error(f"Failed to initialize BiRefNet-Portrait session: {e}", exc_info=True)
            self.session = None
            raise RuntimeError(f"BiRefNet initialization error: {e}")

    def segment_mask(self, image: Image.Image) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Takes a full-resolution PIL RGB image, runs BiRefNet portrait inference,
        and returns:
        - raw_mask: 2D uint8 numpy array (0 = background, 255 = foreground) at original image resolution
        - metadata: Dictionary containing inference timing, resolution, model name
        """
        if self.session is None:
            raise RuntimeError("BiRefNet-Portrait session is not initialized.")

        import rembg

        orig_w, orig_h = image.size
        t0 = time.time()

        # Run inference using persistent session
        # rembg automatically normalizes to 1024x1024 internally and rescales the probability mask back to orig size
        mask_pil = rembg.remove(
            image,
            session=self.session,
            only_mask=True,
            alpha_matting=False,
            post_process_mask=False
        )

        inference_time_ms = int((time.time() - t0) * 1000)

        raw_mask = np.array(mask_pil, dtype=np.uint8)
        if len(raw_mask.shape) == 3:
            raw_mask = raw_mask[:, :, 0]

        # Ensure exact match with original dimensions
        if raw_mask.shape != (orig_h, orig_w):
            raw_mask = np.array(
                Image.fromarray(raw_mask).resize((orig_w, orig_h), Image.Resampling.LANCZOS)
            )

        metadata = {
            "model_name": "BiRefNet-Portrait",
            "checkpoint": "BiRefNet-portrait-epoch_150.onnx",
            "license": "MIT",
            "inference_resolution": "1024x1024",
            "output_resolution": f"{orig_w}x{orig_h}",
            "inference_time_ms": inference_time_ms
        }
        return raw_mask, metadata


# Global singleton instance holder
_birefnet_instance: Optional[BiRefNetPortraitBackend] = None


def get_birefnet_remover() -> BiRefNetPortraitBackend:
    global _birefnet_instance
    if _birefnet_instance is None:
        _birefnet_instance = BiRefNetPortraitBackend()
    return _birefnet_instance
