# Snap2Print (Phase 1)

AI-assisted photo processing tool tailored for small photo studios.
Designed to run efficiently on low-end / standard Windows laptops without requiring a dedicated NVIDIA GPU.

## Phase 1 Features
- **Fast Local Background Removal**: Powered by `u2netp` via ONNX Runtime CPU engine (~4.7MB lightweight model).
- **Session Singleton**: AI model loaded once into memory during startup and reused across requests.
- **Studio Background Presets**:
  - Transparent (clean PNG export)
  - Studio Pure White
  - Passport / ID Blue
  - Custom Studio Color picker & HEX input
- **Instant Recoloring (`/api/photo/recomposite`)**: Swapping background color on an already processed image executes in <20ms without re-running AI segmentation.
- **Before / After Comparison**: Interactive draggable split-view slider and direct preview tabs.
- **Safe Pipeline**: Original customer photo is preserved untouched in `input/`.
- **CPU Throttling Protection**: Proportionally downscales extremely large multi-megapixel raw camera photos for segmentation, preserving the aspect ratio.

## Requirements & Architecture
- Python 3.12+ (64-bit)
- FastAPI + Uvicorn
- Pillow + NumPy
- ONNX Runtime (CPU) + rembg
- Vanilla HTML / CSS / Modern JavaScript (Zero heavy UI frameworks)

## Running Locally

1. Activate virtual environment:
```powershell
.venv\Scripts\Activate.ps1
```

2. Start the local server:
```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

3. Open your browser:
Navigate to `http://127.0.0.1:8000`
