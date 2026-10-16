# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, copy_metadata

block_cipher = None

ROOT_DIR = Path.cwd()

# Core static assets and initial lightweight AI models (~5.2 MB total)
datas = [
    (str(ROOT_DIR / 'frontend'), 'frontend'),
    (str(ROOT_DIR / 'models' / 'face_detection_yunet.onnx'), 'models'),
    (str(ROOT_DIR / 'models' / 'selfie_segmenter.tflite'), 'models'),
    (str(ROOT_DIR / 'models' / 'blaze_face_short_range.tflite'), 'models'),
    (str(ROOT_DIR / 'models' / 'models' / 'u2netp'), 'models/models/u2netp'),
]

# Crucial: Collect package metadata for libraries that call importlib.metadata.version() at runtime
metadata_packages = [
    'pymatting',
    'rembg',
    'pooch',
    'tqdm',
    'jsonschema',
    'jsonschema_specifications',
    'scikit-image',
    'scipy',
    'numpy',
    'pillow',
    'onnxruntime',
    'mediapipe',
    'fastapi',
    'starlette',
    'pydantic',
    'uvicorn',
    'platformdirs',
]

for pkg in metadata_packages:
    try:
        datas += copy_metadata(pkg)
    except Exception as e:
        print(f"Notice during metadata copy for {pkg}: {e}")

binaries = []

hiddenimports = [
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespans',
    'uvicorn.lifespans.on',
    'uvicorn.lifespans.off',
    'python_multipart',
    'multipart',
    'PIL',
    'PIL.Image',
    'PIL.ImageOps',
    'PIL.ImageDraw',
    'PIL.ImageFilter',
    'numpy',
    'cv2',
    'onnxruntime',
    'mediapipe',
    'rembg',
    'pymatting',
    'pymatting.alpha',
    'pymatting.alpha.estimate_alpha_cf',
    'pooch',
    'tqdm',
    'scipy',
    'skimage',
    'backend',
    'backend.main',
    'backend.config',
    'backend.api',
    'backend.api.photo',
    'backend.services',
    'backend.services.face_detection',
    'backend.services.mediapipe_segmentation',
    'backend.services.background_removal',
    'backend.services.background_analyzer',
    'backend.services.chroma_key',
    'backend.services.crop_service',
    'backend.services.image_compositor',
    'backend.services.image_processing',
    'backend.services.mask_refinement',
    'backend.services.birefnet_portrait',
    'backend.utils',
    'backend.utils.image_ops',
]

# Collect hooks from required heavy libraries
for pkg in ['mediapipe', 'onnxruntime', 'cv2', 'rembg', 'pymatting', 'pooch', 'uvicorn', 'fastapi', 'pydantic']:
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception as e:
        print(f"Notice during collection of {pkg}: {e}")

a = Analysis(
    ['launcher.py'],
    pathex=[str(ROOT_DIR)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'pytest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Snap2Print',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Snap2Print',
)
