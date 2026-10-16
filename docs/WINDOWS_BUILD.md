# Windows Standalone Build Guide — Snap2Print

This guide explains how to package the Snap2Print application into a self-contained Windows executable (`Snap2Print.exe`) that non-technical users can launch with a simple double-click without installing Python, pip, Git, or command-line tools.

---

## 1. Development Mode vs. Standalone Packaged Mode

Snap2Print supports two execution environments without any code divergence:

### A. Development Mode
Run directly from source with full live reload and debugging:
```bash
# Activate virtual environment
.venv\Scripts\activate

# Launch via Uvicorn directly
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# Or launch via the unified launcher
python launcher.py
```

### B. Standalone Packaged Mode
Runs as a self-contained Windows executable bundle:
```
dist/
└── Snap2Print/
    ├── Snap2Print.exe          <-- The user double-clicks this
    ├── frontend/               <-- Embedded web UI
    ├── models/                 <-- Bundled core AI models
    ├── input/                  <-- Runtime working directory for uploads
    ├── output/                 <-- Runtime working directory for exports
    └── logs/                   <-- Runtime logs (snap2print.log)
```

---

## 2. Prerequisites for Building

To build the executable from source on a developer PC, you need:
- Windows 10 or 11 (64-bit)
- Python 3.10, 3.11, or 3.12 (64-bit)
- Active project virtual environment (`.venv`) with all dependencies installed:
  ```bash
  pip install -r requirements.txt
  pip install pyinstaller
  ```

---

## 3. How to Build the Windows Executable

### Method 1: One-Click Build Script (Recommended)
Double-click `build_windows.bat` in the repository root, or run:
```cmd
build_windows.bat
```
This script handles temporary cache cleanup, validates dependencies, and compiles the project.

### Method 2: Manual Command Line Build
To invoke PyInstaller directly using the specification file:
```cmd
.venv\Scripts\pyinstaller.exe Snap2Print.spec --workpath "%TEMP%\snap2print_build" --distpath dist -y
```

> **Note on `--workpath`**: Directing the temporary intermediate compiler cache to `%TEMP%` prevents consuming project disk space while compiling large deep learning dependencies like OpenCV, MediaPipe, and ONNX Runtime.

---

## 4. Build Output Location

Once compilation succeeds, the output is located at:
```
dist\Snap2Print\Snap2Print.exe
```

To distribute to an end user:
1. Zip the entire `dist\Snap2Print\` folder (e.g., `Snap2Print-v1.0.0-Windows.zip`).
2. The user extracts the folder anywhere on their PC (e.g., Desktop or Program Files).
3. The user double-clicks `Snap2Print.exe`.
4. The local server starts, binds securely to `127.0.0.1`, and automatically opens the user's default web browser to the studio UI.

---

## 5. How AI Models Are Packaged

Snap2Print bundles core AI models directly into the distribution so the application operates 100% offline out of the box:

| Model | Purpose | Size | Packaging Strategy |
| :--- | :--- | :--- | :--- |
| **YuNet** (`face_detection_yunet.onnx`) | Multi-face detection & landmarks | ~232 KB | Bundled inside `models/` |
| **MediaPipe** (`selfie_segmenter.tflite`) | Fast CPU background segmentation | ~249 KB | Bundled inside `models/` |
| **BlazeFace** (`blaze_face_short_range.tflite`) | Secondary face bounding | ~229 KB | Bundled inside `models/` |
| **U2NetP** (`u2netp.onnx`) | Fallback portrait segmentation | ~4.5 MB | Bundled inside `models/models/u2netp/` |
| **BiRefNet** (`birefnet-portrait.onnx`) | Studio-quality matting | ~972 MB | Optional on-demand download or manual copy to `models/models/birefnet-portrait/` |

### Path Resolution Layer
The path resolution layer in `backend/config.py` detects if the application is frozen (`sys.frozen`). It searches:
1. The external `models/` folder next to `Snap2Print.exe` (allowing studio operators to supply custom or updated weights).
2. The internal bundled `models/` directory inside the PyInstaller package.
3. If a model is not found and internet access is available, it downloads to the local `models/` folder without breaking permissions.

---

## 6. Runtime Working Directories

At runtime, Snap2Print dynamically creates and writes to three folders located in the application directory:
- `input/`: Stores temporary uploaded portraits during an active studio session.
- `output/`: Stores finalized single passport crops and 300 DPI 4×6 print sheets.
- `logs/`: Contains `snap2print.log` for troubleshooting.

---

## 7. Troubleshooting Common Problems

### Problem: Port 8000 is Already in Use
**Solution**: Snap2Print features dynamic port allocation. If port 8000 is occupied by another local service, the launcher automatically scans and binds to the next available port (`8001`, `8002`, etc.) and opens the browser to that exact address.

### Problem: Browser Does Not Open Automatically
**Solution**: If the default browser fails to launch due to system security settings, the console window displays the exact local address (e.g., `http://127.0.0.1:8000`). Simply copy and paste this URL into Chrome, Edge, or Firefox.

### Problem: Windows Defender / SmartScreen Warning
**Solution**: Unsigned executables built from source may trigger a Windows SmartScreen warning ("Windows protected your PC"). Click **More info** -> **Run anyway**. (For production commercial releases, a code-signing certificate should be applied).

---

## 8. Creating a Clean Rebuild

If you update dependencies or modify code and wish to ensure a completely fresh build:
```cmd
:: 1. Remove old distribution and temporary build directories
rmdir /s /q dist\Snap2Print
rmdir /s /q "%TEMP%\snap2print_build"

:: 2. Re-run build
build_windows.bat
```
