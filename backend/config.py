import sys
from pathlib import Path

# Detect frozen (PyInstaller executable) vs. normal development environment
IS_FROZEN = getattr(sys, "frozen", False)

if IS_FROZEN:
    # Running in a PyInstaller bundle
    # BUNDLE_DIR contains read-only bundled assets (frontend, bundled models)
    BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", sys.executable)).resolve()
    # APP_DIR is the directory where the .exe is located (writable for user files)
    APP_DIR = Path(sys.executable).parent.resolve()
else:
    # Normal development mode
    BUNDLE_DIR = Path(__file__).resolve().parent.parent
    APP_DIR = BUNDLE_DIR

BASE_DIR = APP_DIR

# Frontend static files: check bundle first (if packaged), then app dir
if (BUNDLE_DIR / "frontend").exists():
    FRONTEND_DIR = BUNDLE_DIR / "frontend"
else:
    FRONTEND_DIR = APP_DIR / "frontend"

# Runtime working directories (must be writable on user's machine)
INPUT_DIR = APP_DIR / "input"
OUTPUT_DIR = APP_DIR / "output"

# Models directory: check APP_DIR/models first, then BUNDLE_DIR/models
if (APP_DIR / "models").exists():
    MODELS_DIR = APP_DIR / "models"
elif (BUNDLE_DIR / "models").exists():
    MODELS_DIR = BUNDLE_DIR / "models"
else:
    MODELS_DIR = APP_DIR / "models"


def get_model_file(filename: str) -> Path:
    """
    Locates a model file, checking:
    1. APP_DIR/models/filename (external user models folder next to exe)
    2. BUNDLE_DIR/models/filename (internal PyInstaller bundle)
    3. Project repo models directory (when running on machine where repo exists)
    4. Default target: APP_DIR/models/filename (if downloading is needed)
    """
    app_target = APP_DIR / "models" / filename
    if app_target.exists():
        return app_target
    bundle_target = BUNDLE_DIR / "models" / filename
    if bundle_target.exists():
        return bundle_target
    # Fallback to local project directory if running on development machine
    repo_models = Path(__file__).resolve().parent.parent / "models"
    repo_target = repo_models / filename
    if repo_target.exists():
        return repo_target
    return app_target


# Ensure writable runtime directories exist
try:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

# Image Constraints
MAX_FILE_SIZE_MB = 25
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
MAX_DIMENSION = 2048  # Downscale for CPU-friendly inference if larger, preserving aspect ratio

# Background Model Configuration
# 'u2netp' is ~4.7MB, optimized for low-end CPUs and fast turnaround
DEFAULT_BG_MODEL = "u2netp"

