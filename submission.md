# Snap2Print — A Local-First AI Passport Photo Studio

## What I Built

Snap2Print is a local-first, zero-cloud-cost passport photo workstation engineered for neighborhood photo studios, copy centers, visa agencies, and print shops.

### The Problem
Processing passport photos in small storefront studios is burdened by repetitive friction and mounting expenses:
1. **Recurring Cloud Costs**: Commercial background-removal APIs charge anywhere from $0.20 to over $1.00 per processed image, heavily cutting into small studio profit margins.
2. **Biometric Privacy Risks**: Uploading customer portraits, government-bound photos, and children's pictures to third-party cloud servers poses serious legal, regulatory, and privacy concerns.
3. **Heavy Manual Editing**: Photographers routinely spend 10 to 15 minutes per customer in complex editing software manually cropping to foreign aspect ratios, tracing backgrounds, drawing cutting borders, and arranging duplicates on photo paper.
4. **Group Photo Isolation**: When couples or families take group photos together, studios must laboriously crop, frame, and export each subject individually.
5. **Hardware Constraints**: Most deep learning pipelines demand high-end dedicated GPUs with CUDA, whereas most small shops operate on ordinary commodity laptop or desktop CPUs.

### Who It Is For
Snap2Print is built specifically for small studio operators, local print shops, and individuals needing reliable, compliant passport photos without recurring subscription fees or cloud dependencies.

### The Complete User Workflow
Snap2Print streamlines the entire production chain into an intuitive sequence:
1. **Upload & Preprocessing**: The operator uploads an image (portrait or group photo). The system automatically normalizes EXIF camera rotation and validates formatting.
2. **Face Detection**: An on-device neural detector scans the frame, detecting all individuals and locating 5 biometric facial landmarks per person.
3. **Interactive Person Selection**: The operator clicks on any detected individual's face chip to immediately isolate that subject from a group.
4. **AI-Assisted Passport Crop**: The system pre-calculates an official passport crop (supporting standard international `35:45`, US `1:1`, and portrait `3:4` presets) featuring on-screen Eye Line (40%) and Chin Line (70–75%) framing guides.
5. **Manual Crop Adjustment**: The operator can interactively pan and resize the bounding box with a 60 FPS live preview.
6. **Decoupled Background Workflow (Optional)**: 
   - **Keep Original Background**: If the original camera background already meets requirements, the user simply proceeds with **zero AI inference overhead**.
   - **Studio Background Replacement**: If a new background is needed, the system segments **only the cropped portrait** (rather than the entire high-resolution image), maximizing speed and edge quality.
7. **Background Selection & Replacement**: The operator can select standard Studio White, Passport Blue, Transparent, or any custom color with adjustable opacity.
8. **Mask Retouching / Eraser**: A built-in brush tool allows quick touch-ups on segmentation edges (adjustable brush size, hardness, and undo/redo) without re-running any models.
9. **Face Enhancement Controls**: Responsive client-side sliders allow quick adjustments for lighting, skin smoothing, blemish reduction, and sharpening, complete with "Hold for Before" and split-screen comparison modes.
10. **Print-Ready 4×6 Layout**: The finalized passport photo is placed into an automated physical print layout sheet (1200×1800 or 1800×1200 pixels at 300 DPI) with customizable copies, equal spacing, and solid black cutting borders.
11. **Export**: High-resolution download of either the single passport photo or the lab-ready 300 DPI print sheet.

---

## Demo

<!-- PLACEHOLDER: Replace the URL below with your actual demo video or interactive walkthrough link before final publishing -->
[Watch the Snap2Print Demo](https://example.com/snap2print-demo)

*Note on Demo Content: The demo should walk through uploading an original photo containing multiple subjects, isolating a single individual, adjusting the passport crop using the eye and chin alignment guides, selecting an optional studio background, demonstrating the manual brush eraser, and exporting an 8-up 4×6 inch print sheet ready for physical printing.*

---

## Code

The complete source code and project documentation are available in the public repository:

[Snap2Print GitHub Repository](https://github.com/shahilkhan2029/Snap2Print)

The repository includes the FastAPI backend, the lightweight frontend studio, automated test suites, setup scripts, and detailed architecture documentation.

---

## How I Built It

Snap2Print is designed with a lightweight, local-first architecture. It combines specialized local machine learning models with classical computer vision and client-side rendering to run smoothly on standard consumer CPU hardware.

### Technology Stack
- **Backend**: FastAPI (Python 3.10+), Uvicorn, Pillow, NumPy.
- **Frontend**: Vanilla HTML5, CSS3, and JavaScript with 60 FPS HTML5 Canvas rendering—deliberately avoiding heavy frontend frameworks to maintain fast load times and straightforward local deployment.
- **Computer Vision & Inference**: OpenCV (`opencv-python-headless`), ONNX Runtime, Google MediaPipe (`mediapipe`), TensorFlow Lite runtime with XNNPACK CPU acceleration.

### Implemented Architecture & Components
1. **Multi-Face Detection with Biometric Landmarks**:
   - Model: **OpenCV YuNet** (`face_detection_yunet.onnx`, ~232 KB).
   - Detects multiple faces in group shots with bounding coordinates and five facial landmark points (both eyes, nose tip, and mouth corners) in approximately 30–120 ms on a standard CPU.
2. **AI Passport Crop Calculation**:
   - A dedicated Python service converts landmark geometry into standard passport bounding boxes, ensuring that the crown and chin align precisely with international passport conventions (e.g., ICAO 35×45 mm proportions).
3. **Decoupled, Post-Crop Segmentation Pipeline**:
   - Rather than segmenting the entire original multi-megapixel photo upfront, Snap2Print decouples background removal so it only executes on the finalized cropped area, and only when the operator explicitly requests a background swap.
   - **Default Engine**: **Google MediaPipe Selfie Segmenter** (`selfie_segmenter.tflite`, ~249 KB). Executes via TFLite XNNPACK on CPU in ~10–40 ms.
   - **Alternative High-Detail Engine**: **BiRefNet-Portrait** (`birefnet-portrait.onnx`, ~972 MB via ONNX Runtime) for complex hair textures and fine edges.
   - **Fallback Engine**: **U2NetP** (`u2netp.onnx`, ~4.7 MB) for broad compatibility.
   - **Analytical Chroma Keying**: A dedicated HSV color-distance algorithm that isolates solid green or blue studio backdrops in under 5 ms without running neural networks.
4. **Hybrid Mask Refinement & Manual Retouching**:
   - Algorithmic morphological closing and bilateral filtering heal minor edge gaps and eliminate halos.
   - A browser-based raster eraser brush lets the operator manually paint back or remove sections of the mask with full undo/redo state management.
5. **Interactive Face Enhancement Architecture**:
   - Real-time client-side controls allow the operator to adjust master strength, lighting, smoothing, and sharpening, providing immediate visual feedback and split-screen comparison without causing server-side bottlenecks.
6. **Physical 4×6 Print Sheet Engine (300 DPI)**:
   - Built to match standard dye-sublimation and minilab photo paper dimensions (4 × 6 inches at 300 DPI = 1200 × 1800 px portrait or 1800 × 1200 px landscape).
   - An automated grid packing algorithm calculates columns and rows, applies consistent margins, locks the strict passport aspect ratio without horizontal or vertical distortion, and overlays solid black cutting lines around each photo.
7. **Native High-Resolution Compositing & Export**:
   - While interactive previews operate on cached display bitmaps, final exports re-map the user's crop coordinates and mask adjustments onto the uncompressed original source image using high-quality Lanczos resampling.

### Why Blending AI and Classical Computer Vision Matters
Rather than relying on a single large deep learning model for every task, Snap2Print uses a hybrid approach:
- Face detection and organic hair boundary extraction are handled by lightweight neural networks where machine learning excels.
- Solid backdrops (green/blue screen), bounding-box math, aspect-ratio enforcement, and print grid packing are handled by classical computer vision algorithms and geometric math. This hybrid design keeps CPU memory low, speeds up processing, and eliminates unnecessary computation.

---

## Why Open Innovation Matters

Snap2Print illustrates the tangible value of open-source software and open-weight AI models for small businesses and local services:

1. **True Privacy and Data Sovereignty**: Small print shops handle personal identification photos, including those of minors. Running inference locally on the studio workstation means biometric data never leaves the building, ensuring compliance with privacy standards by design.
2. **Eliminating Recurring API Costs**: Commercial cloud vision APIs charge per request. For a neighborhood photo shop operating on thin margins, replacing external APIs with local models eliminates recurring costs entirely.
3. **Predictable Offline Reliability**: Local shops cannot afford customer delays due to internet outages, rate limits, or API downtime. Snap2Print runs completely offline once installed.
4. **Modularity and Model Swapping**: Because the system is built on open standards (ONNX Runtime, TFLite, and OpenCV), studio operators are not locked into any single vendor. If a better open-weight segmentation model is released, it can be dropped into the pipeline without rewriting the application.

### Distinction: Open-Source Software vs. Open-Weight Models
To maintain technical accuracy:
- **Open-Source Software & Architectures**: The application source code, FastAPI, OpenCV, and models like OpenCV YuNet, Google MediaPipe, and U2NetP are licensed under permissive open-source licenses (Apache 2.0 / MIT).
- **Open-Weight Models**: Research models such as BiRefNet-Portrait are open-weight models provided for open academic and commercial use under their respective release terms (MIT license). They provide transparent, inspectable weights without proprietary cloud black boxes.

---

## Optional: My Agent Session

<!-- PLACEHOLDER: If you documented your build or development workflow in an AI agent session transcript, replace the URL below -->
[View Agent Session](https://example.com/agent-session)

*Note: This link is a placeholder to be updated with an exported session transcript or recording if desired.*

---

## Optional: My First User

*This section is intentionally omitted as no verified first-user or customer case study is documented in the repository. In accordance with competition guidelines, no fictional testimonials or users have been fabricated.*

---

## Prize Categories

### Primary Alignment: Open-Source / Local-First Innovation
Snap2Print is submitted as a fully open-source, local-first utility demonstrating how open-weight AI models and classical computer vision can run on commodity consumer hardware to solve real-world operational problems for small businesses.

### Partner Prize Categories
*Transparency Notice*: Snap2Print does not integrate commercial cloud sponsor APIs (such as MongoDB Atlas, ElevenLabs, Temporal, Sentry, SerpApi, TabPFN, Gemma, or DigitalOcean) because the explicit design goal of the application is **zero-cloud, offline-capable, CPU-only local execution**. Furthermore, GitHub Copilot is not claimed as a category unless specifically verified in the commit history. Therefore, no unverified partner categories are claimed.

---

## Technical Highlights

- **Multi-Face Group Isolation**: Detects all faces in a photo and allows instant one-click selection of an individual subject.
- **Biometric Passport Guidelines**: Automatically calculates 35:45, 1:1, and 3:4 crops with eye-line (40%) and chin-line (70–75%) on-screen framing guides.
- **Real-Time Interactive Framing**: Smooth live canvas preview updating at 60 FPS with manual boundary controls.
- **Decoupled Background Architecture**: Background removal is completely optional; if the original background is retained, inference overhead is 0 ms.
- **4-Tier Segmentation Engine**: Integrates MediaPipe (~10–40 ms on CPU), BiRefNet-Portrait for fine hair detail, U2NetP for fallback, and Analytical HSV Chroma Key (<5 ms).
- **Manual Mask Retouching**: Brush eraser tool with adjustable size, hardness, and full undo/redo state management.
- **Live Face Enhancement Preview**: Instant before/after and split-screen comparison for lighting, skin smoothing, and sharpness tuning.
- **300 DPI 4×6 Print Sheet Engine**: Mathematical grid tiling for physical photo paper with equal margins and crisp black cutting borders.
- **High-Resolution Dual Export**: Generates full-resolution single passport photos as well as print-ready 300 DPI sheets (1200×1800 px).
- **Zero API Keys & Zero Telemetry**: Fully air-gapped capable; no cloud dependencies or external data transmission.

---

## Submission Checklist

- [ ] Replace demo URL with final video URL
- [ ] Verify GitHub repository URL
- [ ] Add actual Agent Session URL if applicable
- [ ] Verify any claimed prize categories
- [ ] Review screenshots/demo
- [ ] Final proofreading before publishing
