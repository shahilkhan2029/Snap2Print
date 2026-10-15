from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
MODELS_DIR = BASE_DIR / "models"
FRONTEND_DIR = BASE_DIR / "frontend"

# Ensure directories exist
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Image Constraints
MAX_FILE_SIZE_MB = 25
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
MAX_DIMENSION = 2048  # Downscale for CPU-friendly inference if larger, preserving aspect ratio

# Background Model Configuration
# 'u2netp' is ~4.7MB, optimized for low-end CPUs and fast turnaround
DEFAULT_BG_MODEL = "u2netp"
