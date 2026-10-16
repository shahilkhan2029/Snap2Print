from abc import ABC, abstractmethod
import logging
import os
import time
from typing import Optional, Tuple, Dict, Any
from PIL import Image
import numpy as np

from backend.config import DEFAULT_BG_MODEL, MODELS_DIR, get_model_file

logger = logging.getLogger(__name__)


class BaseBackgroundRemover(ABC):
    """Abstract interface for modular background removal backends."""

    @abstractmethod
    def segment_mask(self, image: Image.Image) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Takes a PIL RGB image and returns:
        - raw_mask: 2D uint8 numpy array (0 = background, 255 = foreground)
        - metadata: Dictionary containing timing, model name, etc.
        """
        pass


class RembgU2NetPBackend(BaseBackgroundRemover):
    """
    Lightweight, CPU-optimized rembg backend using 'u2netp' (~4.7MB).
    Loaded once and reused across all incoming requests.
    """

    def __init__(self, model_name: str = DEFAULT_BG_MODEL):
        self.model_name = model_name
        self.session = None
        self._initialize_session()

    def _initialize_session(self):
        try:
            u2net_path = get_model_file(f"models/{self.model_name}/{self.model_name}.onnx")
            if u2net_path.exists():
                os.environ["U2NET_HOME"] = str(u2net_path.parent.parent.parent)
            else:
                os.environ["U2NET_HOME"] = str(MODELS_DIR)
            import rembg

            logger.info(f"Initializing singleton background removal session with model: '{self.model_name}'...")
            self.session = rembg.new_session(self.model_name)
            logger.info("Background removal model loaded successfully into memory.")
        except Exception as e:
            logger.error(f"Failed to load background model '{self.model_name}': {e}", exc_info=True)
            self.session = None
            raise RuntimeError(
                f"Background removal model initialization failed. Error: {e}"
            )

    def segment_mask(self, image: Image.Image) -> Tuple[np.ndarray, Dict[str, Any]]:
        if self.session is None:
            raise RuntimeError("Model session is not initialized.")

        import rembg

        t0 = time.time()
        # only_mask=True directly returns the single-channel L mask from rembg
        mask_pil = rembg.remove(
            image,
            session=self.session,
            only_mask=True,
            alpha_matting=False,
            post_process_mask=False  # We do superior edge refinement in mask_refinement.py
        )
        inference_time_ms = int((time.time() - t0) * 1000)

        raw_mask = np.array(mask_pil, dtype=np.uint8)
        if len(raw_mask.shape) == 3:
            raw_mask = raw_mask[:, :, 0]

        metadata = {
            "model_name": self.model_name,
            "inference_time_ms": inference_time_ms
        }
        return raw_mask, metadata


# Singleton instance holder
_model_instance: Optional[BaseBackgroundRemover] = None


def get_background_remover() -> BaseBackgroundRemover:
    global _model_instance
    if _model_instance is None:
        _model_instance = RembgU2NetPBackend()
    return _model_instance
