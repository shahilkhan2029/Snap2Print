// Snap2Print Studio Logic
// Streamlined Workflow: Upload -> Face Detection -> Select Person -> Passport Crop (Live Synced Preview) -> Optional Background Removal -> Export

document.addEventListener("DOMContentLoaded", () => {
  // --- DOM Elements ---
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const browseBtn = document.getElementById("browseBtn");
  const dropzoneContent = document.getElementById("dropzoneContent");
  const fileInfoBar = document.getElementById("fileInfoBar");
  const fileName = document.getElementById("fileName");
  const fileSize = document.getElementById("fileSize");
  const clearFileBtn = document.getElementById("clearFileBtn");

  // Person Selector & Crop Panels
  const personSelectCard = document.getElementById("personSelectCard");
  const personChipsList = document.getElementById("personChipsList");
  const cropControlsCard = document.getElementById("cropControlsCard");
  const ratioPills = document.querySelectorAll(".ratio-pill");
  const resetCropBtn = document.getElementById("resetCropBtn");
  const zoomInBtn = document.getElementById("zoomInBtn");
  const zoomOutBtn = document.getElementById("zoomOutBtn");

  // Step 5: Background Choice Elements
  const backgroundChoiceCard = document.getElementById("backgroundChoiceCard");
  const btnKeepOriginalBg = document.getElementById("btnKeepOriginalBg");
  const btnRemoveBg = document.getElementById("btnRemoveBg");
  const originalBgInfo = document.getElementById("originalBgInfo");
  const removeBgControls = document.getElementById("removeBgControls");
  const runBgRemovalBtn = document.getElementById("runBgRemovalBtn");
  const runBgSpinner = document.getElementById("runBgSpinner");
  const runBgBtnText = document.getElementById("runBgBtnText");

  const methodBanner = document.getElementById("methodBanner");
  const methodLabel = document.getElementById("methodLabel");
  const methodSub = document.getElementById("methodSub");
  const methodModeSelect = document.getElementById("methodModeSelect");
  const smoothnessSlider = document.getElementById("smoothnessSlider");
  const smoothnessVal = document.getElementById("smoothnessVal");
  const bgOptions = document.querySelectorAll(".bg-option-item");
  const customColorContainer = document.getElementById("customColorContainer");
  const colorPickerInput = document.getElementById("colorPickerInput");
  const colorHexInput = document.getElementById("colorHexInput");
  const colorOpacitySlider = document.getElementById("colorOpacitySlider");
  const colorOpacityVal = document.getElementById("colorOpacityVal");
  const customColorSwatch = document.getElementById("customColorSwatch");

  // Step 5b: Manual Eraser Retouch Tool
  const eraserToolCard = document.getElementById("eraserToolCard");
  const btnToggleEraser = document.getElementById("btnToggleEraser");
  const eraserToggleText = document.getElementById("eraserToggleText");
  const eraserControlsBody = document.getElementById("eraserControlsBody");
  const eraserSizeSlider = document.getElementById("eraserSizeSlider");
  const eraserSizeVal = document.getElementById("eraserSizeVal");
  const eraserHardnessSlider = document.getElementById("eraserHardnessSlider");
  const eraserHardnessVal = document.getElementById("eraserHardnessVal");
  const btnEraserUndo = document.getElementById("btnEraserUndo");
  const btnEraserRedo = document.getElementById("btnEraserRedo");
  const btnEraserReset = document.getElementById("btnEraserReset");
  const eraserBrushCursor = document.getElementById("eraserBrushCursor");

  // Step 6: Face Enhancement Elements
  const faceEnhancementCard = document.getElementById("faceEnhancementCard");
  const toggleEnhancement = document.getElementById("toggleEnhancement");
  const enhancementStatusLabel = document.getElementById("enhancementStatusLabel");
  const enhancementBody = document.getElementById("enhancementBody");
  const enhancementStrengthSlider = document.getElementById("enhancementStrengthSlider");
  const enhancementStrengthVal = document.getElementById("enhancementStrengthVal");
  const enhancementLightingSlider = document.getElementById("enhancementLightingSlider");
  const enhancementLightingVal = document.getElementById("enhancementLightingVal");
  const enhancementSmoothingSlider = document.getElementById("enhancementSmoothingSlider");
  const enhancementSmoothingVal = document.getElementById("enhancementSmoothingVal");
  const enhancementBlemishSlider = document.getElementById("enhancementBlemishSlider");
  const enhancementBlemishVal = document.getElementById("enhancementBlemishVal");
  const enhancementSharpeningSlider = document.getElementById("enhancementSharpeningSlider");
  const enhancementSharpeningVal = document.getElementById("enhancementSharpeningVal");
  const presetBtns = document.querySelectorAll(".preset-btn[data-preset]");
  const btnResetEnhancement = document.getElementById("btnResetEnhancement");
  const btnCompareHold = document.getElementById("btnCompareHold");
  const btnCompareToggle = document.getElementById("btnCompareToggle");
  const enhancementCompareTag = document.getElementById("enhancementCompareTag");

  // Step 7: Export Panels & Buttons
  const exportCard = document.getElementById("exportCard");
  const downloadPanelBtn = document.getElementById("downloadPanelBtn");
  const downloadBtn = document.getElementById("downloadBtn");
  const downloadBtnText = document.getElementById("downloadBtnText");
  const downloadSpinner = document.getElementById("downloadSpinner");
  const downloadIcon = document.getElementById("downloadIcon");

  // Step 8: Print-Ready 4x6 Layout Elements
  const printLayoutCard = document.getElementById("printLayoutCard");
  const btnOrientPortrait = document.getElementById("btnOrientPortrait");
  const btnOrientLandscape = document.getElementById("btnOrientLandscape");
  const printCopiesInput = document.getElementById("printCopiesInput");
  const printCopiesVal = document.getElementById("printCopiesVal");
  const btnCopiesMinus = document.getElementById("btnCopiesMinus");
  const btnCopiesPlus = document.getElementById("btnCopiesPlus");
  const btnMaxFit = document.getElementById("btnMaxFit");
  const printBorderSlider = document.getElementById("printBorderSlider");
  const printBorderVal = document.getElementById("printBorderVal");
  const printSpacingSlider = document.getElementById("printSpacingSlider");
  const printSpacingVal = document.getElementById("printSpacingVal");
  const printMarginSlider = document.getElementById("printMarginSlider");
  const printMarginVal = document.getElementById("printMarginVal");
  const printGridLabel = document.getElementById("printGridLabel");
  const printRatioLabel = document.getElementById("printRatioLabel");
  const btnDownload4x6 = document.getElementById("btnDownload4x6");
  const download4x6Spinner = document.getElementById("download4x6Spinner");
  const download4x6BtnText = document.getElementById("download4x6BtnText");

  // Print-Ready 4x6 Sheet Viewport Elements
  const tabPrint = document.getElementById("tabPrint");
  const printViewportContainer = document.getElementById("printViewportContainer");
  const printSheetCanvasArea = document.getElementById("printSheetCanvasArea");
  const printSheetPaperCard = document.getElementById("printSheetPaperCard");
  const printSheetCanvas = document.getElementById("printSheetCanvas");
  const sheetDimTag = document.getElementById("sheetDimTag");
  const sheetPaperWatermark = document.getElementById("sheetPaperWatermark");
  const btnSwitchToPassport = document.getElementById("btnSwitchToPassport");

  // Viewport & Live Passport Card Elements
  const emptyState = document.getElementById("emptyState");
  const dualPanelContainer = document.getElementById("dualPanelContainer");
  const originalFrame = document.getElementById("originalFrame");
  const imgOriginal = document.getElementById("imgOriginal");
  const faceStatusBadge = document.getElementById("faceStatusBadge");
  const faceBadgeText = document.getElementById("faceBadgeText");
  const faceOverlaysContainer = document.getElementById("faceOverlaysContainer");

  const cropOverlayWrapper = document.getElementById("cropOverlayWrapper");
  const cropBox = document.getElementById("cropBox");
  const cropBoxBadge = document.getElementById("cropBoxBadge");
  const cropHandles = document.querySelectorAll(".crop-handle");

  // Passport Preview Card & Live Canvas
  const passportPhotoCard = document.getElementById("passportPhotoCard");
  const passportPreviewCanvas = document.getElementById("passportPreviewCanvas");
  const passportSpecTag = document.getElementById("passportSpecTag");
  const processedStatusBadge = document.getElementById("processedStatusBadge");

  // Telemetry Elements
  const debugCard = document.getElementById("debugCard");
  const dbgSeg = document.getElementById("dbgSeg");
  const dbgRefine = document.getElementById("dbgRefine");
  const dbgColorLatency = document.getElementById("dbgColorLatency");
  const dbgExport = document.getElementById("dbgExport");
  const dbgPreviewRes = document.getElementById("dbgPreviewRes");
  const dbgExportRes = document.getElementById("dbgExportRes");

  // View Tabs
  const tabOriginal = document.getElementById("tabOriginal");
  const tabProcessed = document.getElementById("tabProcessed");
  const tabSplit = document.getElementById("tabSplit");

  // Overlays
  const processingOverlay = document.getElementById("processingOverlay");
  const processingStateMsg = document.getElementById("processingStateMsg");
  const progressFill = document.getElementById("progressFill");
  const errorToast = document.getElementById("errorToast");
  const errorMessage = document.getElementById("errorMessage");
  const toastClose = document.getElementById("toastClose");

  // --- Aspect Ratio Lookup ---
  const RATIO_VALUES = {
    "35:45": 35.0 / 45.0,  // Standard Passport (~0.7778)
    "1:1": 1.0,            // US Passport (1.0)
    "3:4": 3.0 / 4.0       // Visa / Portrait (0.75)
  };

  const RATIO_CSS = {
    "35:45": "35 / 45",
    "1:1": "1 / 1",
    "3:4": "3 / 4"
  };

  // --- Client State ---
  const memoryCache = {
    currentFile: null,
    sessionId: null,
    bgMode: "original",         // "original" (Default • No AI) | "remove" (Studio Colors)
    activeBgChoice: "transparent",
    activeCustomColor: "#1877f2",
    activeCustomOpacity: 100,
    originalDimensions: null,
    previewDimensions: null,
    faceDetection: null,
    selectedFaceId: null,
    activeRatioName: "35:45",
    activeRatioVal: 35.0 / 45.0,
    cropNorm: { x: 0.2, y: 0.15, w: 0.55, h: 0.70 }, // Normalized coordinates (0..1)
    transparentSubjectImg: null, // Image object of segmented transparent subject
    currentViewMode: "split",

    // Manual Eraser Retouch State
    eraserActive: false,
    eraserSize: 25,
    eraserHardness: 0.4,
    isErasing: false,
    lastEraserPoint: null,
    maskEdited: false,
    rawCroppedImg: null,
    maskCanvas: null,
    maskCtx: null,
    originalMaskCanvas: null,
    subjectCanvas: null,
    subjectCtx: null,
    undoStack: [],
    redoStack: [],

    // Step 6: Face Enhancement State (UI & Instant Preview Architecture)
    faceEnhancement: {
      enabled: false,
      strength: 50,
      lighting: 10,
      smoothing: 35,
      blemish: 25,
      sharpening: 20,
      compareMode: false,
      splitCompare: false
    },

    // Step 8: Print-Ready 4x6 Layout State
    printLayout: {
      orientation: "portrait", // "portrait" (1200x1800) | "landscape" (1800x1200)
      copies: 8,
      borderPx: 2,
      spacingPx: 20,
      marginPx: 30,
      maxFit: 8,
      cols: 2,
      rows: 4
    }
  };

  // --- 1. File Upload & Drag-and-Drop ---
  browseBtn.addEventListener("click", () => fileInput.click());
  dropzone.addEventListener("click", (e) => {
    if (e.target !== clearFileBtn && !clearFileBtn.contains(e.target) && !memoryCache.currentFile) {
      fileInput.click();
    }
  });

  ["dragenter", "dragover"].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove("dragover");
    });
  });

  dropzone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) handleFile(files[0]);
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) handleFile(e.target.files[0]);
  });

  clearFileBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    resetState();
  });

  function handleFile(file) {
    const valid = [".jpg", ".jpeg", ".png", ".webp", ".bmp"];
    const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
    if (!valid.includes(ext)) {
      showError(`Unsupported format '${ext}'. Please choose a JPG, PNG, WEBP, or BMP.`);
      return;
    }
    if (file.size > 25 * 1024 * 1024) {
      showError("File size exceeds 25 MB limit.");
      return;
    }

    memoryCache.currentFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB`;
    fileInfoBar.classList.remove("hidden");
    dropzoneContent.classList.add("hidden");
    hideError();

    // Trigger Step 1 & 2: Upload & Multi-Face Detection
    uploadAndDetect(file);
  }

  // --- STEP 1 & 2: Upload & Face Detection (Zero Background Removal) ---
  async function uploadAndDetect(file) {
    showOverlay(true);
    setStage("Uploading photo & detecting faces...", 35);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/api/photo/upload-and-detect", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Upload & detection failed.");

      memoryCache.sessionId = data.session_id;
      memoryCache.originalDimensions = data.original_dimensions;
      memoryCache.previewDimensions = data.preview_dimensions;
      memoryCache.faceDetection = data.face_detection;
      memoryCache.bgMode = "original"; // Default: Keep original background
      memoryCache.transparentSubjectImg = null;

      // Unhide panels & show image
      emptyState.classList.add("hidden");
      dualPanelContainer.classList.remove("hidden");
      imgOriginal.src = data.preview_url;

      // Handle Detected Faces
      const fd = data.face_detection || {};
      const faces = fd.faces || [];
      const count = fd.face_count || (fd.detected ? 1 : 0);

      if (count > 0 && faces.length > 0) {
        faceStatusBadge.classList.remove("hidden", "no-face");
        faceBadgeText.textContent = count > 1 ? `${count} faces detected` : `Face detected (${Math.round((faces[0].confidence || 0.9) * 100)}%)`;

        renderPersonChips(faces);
        personSelectCard.classList.remove("hidden");

        // Select primary face
        selectPerson(faces[0].id);
      } else {
        faceStatusBadge.classList.remove("hidden");
        faceStatusBadge.classList.add("no-face");
        faceBadgeText.textContent = "No face detected";
        personSelectCard.classList.add("hidden");

        const defCrop = fd.default_crop || { x_norm: 0.15, y_norm: 0.15, w_norm: 0.7, h_norm: 0.7 / memoryCache.activeRatioVal };
        memoryCache.cropNorm = {
          x: defCrop.x_norm,
          y: defCrop.y_norm,
          w: defCrop.w_norm,
          h: defCrop.h_norm
        };
        updateCropBoxDOM();
        updateLivePassportPreview();
      }

      // Show Workflow Steps
      cropControlsCard.classList.remove("hidden");
      backgroundChoiceCard.classList.remove("hidden");
      if (faceEnhancementCard) faceEnhancementCard.classList.remove("hidden");
      exportCard.classList.remove("hidden");
      if (printLayoutCard) printLayoutCard.classList.remove("hidden");
      cropOverlayWrapper.classList.remove("hidden");

      // Enable Download immediately with original background
      downloadBtn.classList.remove("disabled");
      setBgMode("original");

      setViewMode("split");
    } catch (err) {
      showError(err.message || "Failed to upload photo.");
    } finally {
      showOverlay(false);
    }
  }

  // --- Render Person Selector Chips ---
  function renderPersonChips(faces) {
    personChipsList.innerHTML = "";
    faces.forEach((face) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "person-chip";
      chip.setAttribute("data-face-id", face.id);

      const confPct = Math.round((face.confidence || 0) * 100);
      chip.innerHTML = `
        <span class="person-chip-avatar">👤</span>
        <div class="person-chip-info">
          <span class="person-chip-name">${face.label || `Face ${face.id}`}</span>
          <span class="person-chip-conf">${confPct}% confidence</span>
        </div>
      `;

      chip.addEventListener("click", () => selectPerson(face.id));
      personChipsList.appendChild(chip);
    });
  }

  // --- Select Person & Auto-Crop Framing ---
  function selectPerson(faceId) {
    memoryCache.selectedFaceId = faceId;
    memoryCache.transparentSubjectImg = null; // New person selected

    // Highlight chip
    const chips = personChipsList.querySelectorAll(".person-chip");
    chips.forEach((c) => {
      const fid = parseInt(c.getAttribute("data-face-id"));
      c.classList.toggle("active", fid === faceId);
    });

    // Highlight face box on photo
    const faceBoxes = faceOverlaysContainer.querySelectorAll(".face-box-overlay");
    faceBoxes.forEach((b) => {
      const fid = parseInt(b.getAttribute("data-face-id"));
      b.classList.toggle("selected", fid === faceId);
    });

    // Auto-align passport crop around selected face
    const fd = memoryCache.faceDetection;
    if (fd && fd.faces) {
      const face = fd.faces.find((f) => f.id === faceId);
      if (face && face.auto_crop) {
        const ac = face.auto_crop;
        memoryCache.cropNorm = {
          x: ac.x_norm,
          y: ac.y_norm,
          w: ac.w_norm,
          h: ac.h_norm
        };
        updateCropBoxDOM();
        updateLivePassportPreview();
      }
    }
  }

  // --- Step 4: Aspect Ratio Selector Pills ---
  ratioPills.forEach((pill) => {
    pill.addEventListener("click", () => {
      ratioPills.forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");

      const ratioName = pill.getAttribute("data-ratio");
      setAspectRatio(ratioName);
    });
  });

  function setAspectRatio(ratioName) {
    memoryCache.activeRatioName = ratioName;
    memoryCache.activeRatioVal = RATIO_VALUES[ratioName] || (35.0 / 45.0);
    cropBoxBadge.textContent = `Passport ${ratioName}`;

    // Update passport card aspect ratio in CSS
    passportPhotoCard.style.aspectRatio = RATIO_CSS[ratioName] || "35 / 45";
    passportSpecTag.textContent = ratioName === "35:45" ? "Standard 35×45 mm" : (ratioName === "1:1" ? "US Passport 2×2 in" : "Visa 3:4");
    processedStatusBadge.textContent = ratioName === "35:45" ? "35×45 mm" : (ratioName === "1:1" ? "2×2 in" : "3:4");

    // Recalculate crop dimensions around current center point
    const currentCrop = memoryCache.cropNorm;
    const centerX = currentCrop.x + currentCrop.w / 2;
    const centerY = currentCrop.y + currentCrop.h / 2;

    const imgW = memoryCache.originalDimensions?.width || 1000;
    const imgH = memoryCache.originalDimensions?.height || 1000;
    const imgAspect = imgW / imgH;
    const normRatioFactor = memoryCache.activeRatioVal / imgAspect;

    let newNormH = currentCrop.h;
    let newNormW = newNormH * normRatioFactor;

    if (newNormW > 1.0) {
      newNormW = 1.0;
      newNormH = newNormW / normRatioFactor;
    }
    if (newNormH > 1.0) {
      newNormH = 1.0;
      newNormW = newNormH * normRatioFactor;
    }

    let newX = centerX - newNormW / 2;
    let newY = centerY - newNormH / 2;

    newX = Math.max(0, Math.min(newX, 1.0 - newNormW));
    newY = Math.max(0, Math.min(newY, 1.0 - newNormH));

    memoryCache.cropNorm = { x: newX, y: newY, w: newNormW, h: newNormH };
    memoryCache.transparentSubjectImg = null; // Ratio changed
    updateCropBoxDOM();
    updateLivePassportPreview();
  }

  // --- Reset to AI Auto-Crop ---
  resetCropBtn.addEventListener("click", () => {
    if (memoryCache.selectedFaceId && memoryCache.faceDetection) {
      selectPerson(memoryCache.selectedFaceId);
    }
  });

  // --- Zoom In / Zoom Out ---
  zoomInBtn.addEventListener("click", () => adjustCropZoom(0.92));  // Tighter
  zoomOutBtn.addEventListener("click", () => adjustCropZoom(1.08)); // Wider

  function adjustCropZoom(factor) {
    const cur = memoryCache.cropNorm;
    const centerX = cur.x + cur.w / 2;
    const centerY = cur.y + cur.h / 2;

    let newW = cur.w * factor;
    let newH = cur.h * factor;

    if (newW < 0.15 || newH < 0.15) return;
    if (newW > 1.0 || newH > 1.0) {
      const maxScale = Math.min(1.0 / cur.w, 1.0 / cur.h);
      newW = cur.w * maxScale;
      newH = cur.h * maxScale;
    }

    let newX = centerX - newW / 2;
    let newY = centerY - newH / 2;

    newX = Math.max(0, Math.min(newX, 1.0 - newW));
    newY = Math.max(0, Math.min(newY, 1.0 - newH));

    memoryCache.cropNorm = { x: newX, y: newY, w: newW, h: newH };
    memoryCache.transparentSubjectImg = null; // Zoom changed
    updateCropBoxDOM();
    updateLivePassportPreview();
  }

  // --- Real-time Interactive Crop Dragging & Resizing ---
  let dragMode = null; // null | "move" | "nw" | "ne" | "se" | "sw"
  let startX = 0, startY = 0;
  let initialCrop = null;

  cropBox.addEventListener("mousedown", (e) => {
    if (e.target.classList.contains("crop-handle")) return;
    dragMode = "move";
    startX = e.clientX;
    startY = e.clientY;
    initialCrop = { ...memoryCache.cropNorm };
    e.preventDefault();
  });

  cropHandles.forEach((handle) => {
    handle.addEventListener("mousedown", (e) => {
      dragMode = handle.getAttribute("data-dir");
      startX = e.clientX;
      startY = e.clientY;
      initialCrop = { ...memoryCache.cropNorm };
      e.stopPropagation();
      e.preventDefault();
    });
  });

  window.addEventListener("mousemove", (e) => {
    if (!dragMode) return;

    const frameRect = getRenderedImageRect();
    if (!frameRect || frameRect.renderedW <= 0 || frameRect.renderedH <= 0) return;

    const deltaXNorm = (e.clientX - startX) / frameRect.renderedW;
    const deltaYNorm = (e.clientY - startY) / frameRect.renderedH;

    const imgW = memoryCache.originalDimensions?.width || 1000;
    const imgH = memoryCache.originalDimensions?.height || 1000;
    const imgAspect = imgW / imgH;
    const normRatioFactor = memoryCache.activeRatioVal / imgAspect;

    if (dragMode === "move") {
      let nextX = initialCrop.x + deltaXNorm;
      let nextY = initialCrop.y + deltaYNorm;
      nextX = Math.max(0, Math.min(nextX, 1.0 - initialCrop.w));
      nextY = Math.max(0, Math.min(nextY, 1.0 - initialCrop.h));
      memoryCache.cropNorm.x = nextX;
      memoryCache.cropNorm.y = nextY;
    } else {
      let scaleChange = 0;
      if (dragMode === "se") {
        scaleChange = Math.max(deltaXNorm / initialCrop.w, deltaYNorm / initialCrop.h);
      } else if (dragMode === "nw") {
        scaleChange = Math.max(-deltaXNorm / initialCrop.w, -deltaYNorm / initialCrop.h);
      } else if (dragMode === "ne") {
        scaleChange = Math.max(deltaXNorm / initialCrop.w, -deltaYNorm / initialCrop.h);
      } else if (dragMode === "sw") {
        scaleChange = Math.max(-deltaXNorm / initialCrop.w, deltaYNorm / initialCrop.h);
      }

      let newH = Math.max(0.15, Math.min(1.0, initialCrop.h * (1.0 + scaleChange)));
      let newW = newH * normRatioFactor;

      if (newW > 1.0) {
        newW = 1.0;
        newH = newW / normRatioFactor;
      }

      let newX = initialCrop.x;
      let newY = initialCrop.y;

      if (dragMode === "nw") {
        newX = initialCrop.x + (initialCrop.w - newW);
        newY = initialCrop.y + (initialCrop.h - newH);
      } else if (dragMode === "ne") {
        newY = initialCrop.y + (initialCrop.h - newH);
      } else if (dragMode === "sw") {
        newX = initialCrop.x + (initialCrop.w - newW);
      }

      if (newX >= 0 && newY >= 0 && newX + newW <= 1.0 && newY + newH <= 1.0) {
        memoryCache.cropNorm = { x: newX, y: newY, w: newW, h: newH };
      }
    }

    // Live continuous synchronization
    memoryCache.transparentSubjectImg = null; // Position shifted
    updateCropBoxDOM();
    updateLivePassportPreview();
  });

  window.addEventListener("mouseup", () => {
    dragMode = null;
  });

  // Calculate rendered image position inside originalFrame
  function getRenderedImageRect() {
    const img = imgOriginal;
    if (!img || !img.complete || img.naturalWidth === 0) return null;

    const frame = img.parentElement;
    if (!frame) return null;

    const frameW = frame.clientWidth;
    const frameH = frame.clientHeight;
    if (frameW <= 0 || frameH <= 0) return null;

    const naturalW = img.naturalWidth;
    const naturalH = img.naturalHeight;
    const imgAspect = naturalW / naturalH;
    const frameAspect = frameW / frameH;

    let renderedW, renderedH, offsetX, offsetY;
    if (frameAspect > imgAspect) {
      renderedH = frameH;
      renderedW = frameH * imgAspect;
      offsetX = (frameW - renderedW) / 2;
      offsetY = 0;
    } else {
      renderedW = frameW;
      renderedH = frameW / imgAspect;
      offsetX = 0;
      offsetY = (frameH - renderedH) / 2;
    }

    return { renderedW, renderedH, offsetX, offsetY };
  }

  function updateCropBoxDOM() {
    const rect = getRenderedImageRect();
    if (!rect) return;

    const cn = memoryCache.cropNorm;
    const boxX = rect.offsetX + cn.x * rect.renderedW;
    const boxY = rect.offsetY + cn.y * rect.renderedH;
    const boxW = cn.w * rect.renderedW;
    const boxH = cn.h * rect.renderedH;

    cropBox.style.left = `${Math.round(boxX)}px`;
    cropBox.style.top = `${Math.round(boxY)}px`;
    cropBox.style.width = `${Math.round(boxW)}px`;
    cropBox.style.height = `${Math.round(boxH)}px`;
  }

  // Pre-generate reusable 32x32 transparency checker pattern
  const checkerCanvas = document.createElement("canvas");
  checkerCanvas.width = 32;
  checkerCanvas.height = 32;
  const cCtx = checkerCanvas.getContext("2d");
  cCtx.fillStyle = "#ffffff";
  cCtx.fillRect(0, 0, 32, 32);
  cCtx.fillStyle = "#cbd5e1";
  cCtx.fillRect(0, 0, 16, 16);
  cCtx.fillRect(16, 16, 16, 16);

  function drawCheckerboard(targetCtx, w, h) {
    const pattern = targetCtx.createPattern(checkerCanvas, "repeat");
    targetCtx.fillStyle = pattern;
    targetCtx.fillRect(0, 0, w, h);
  }

  // Offscreen buffer canvas for zero-flicker composite rendering
  const baseCanvas = document.createElement("canvas");
  const baseCtx = baseCanvas.getContext("2d");

  // --- LIVE SYNCHRONIZED PASSPORT PREVIEW RENDERING (<0.5 ms) ---
  function updateLivePassportPreview() {
    if (!passportPreviewCanvas || !imgOriginal || !imgOriginal.complete) return;
    const nw = imgOriginal.naturalWidth;
    const nh = imgOriginal.naturalHeight;
    if (!nw || !nh) return;

    const cn = memoryCache.cropNorm;
    const srcX = Math.round(cn.x * nw);
    const srcY = Math.round(cn.y * nh);
    const srcW = Math.round(cn.w * nw);
    const srcH = Math.round(cn.h * nh);

    if (srcW <= 0 || srcH <= 0) return;

    // Match canvas buffer dimensions to exact crop pixel resolution
    if (passportPreviewCanvas.width !== srcW || passportPreviewCanvas.height !== srcH) {
      passportPreviewCanvas.width = srcW;
      passportPreviewCanvas.height = srcH;
    }
    if (baseCanvas.width !== srcW || baseCanvas.height !== srcH) {
      baseCanvas.width = srcW;
      baseCanvas.height = srcH;
    }

    baseCtx.clearRect(0, 0, srcW, srcH);

    // 1. Render Base Layer into offscreen baseCanvas
    if (memoryCache.bgMode === "original" || !memoryCache.transparentSubjectImg) {
      baseCtx.drawImage(imgOriginal, srcX, srcY, srcW, srcH, 0, 0, srcW, srcH);
    } else {
      const targetColor = getActiveBgColor();
      if (targetColor === "transparent") {
        drawCheckerboard(baseCtx, srcW, srcH);
      } else {
        if (memoryCache.activeBgChoice === "custom" && memoryCache.activeCustomOpacity < 100) {
          drawCheckerboard(baseCtx, srcW, srcH);
        }
        baseCtx.fillStyle = targetColor;
        baseCtx.fillRect(0, 0, srcW, srcH);
      }
      baseCtx.drawImage(memoryCache.transparentSubjectImg, 0, 0, srcW, srcH);
    }

    // 2. Render onto passportPreviewCanvas with Face Enhancement Preview Architecture
    const ctx = passportPreviewCanvas.getContext("2d");
    ctx.clearRect(0, 0, srcW, srcH);

    const fe = memoryCache.faceEnhancement;

    if (!fe.enabled || fe.compareMode) {
      // Unenhanced state (or user holding "Hold for Before" comparison button)
      ctx.drawImage(baseCanvas, 0, 0);
    } else {
      // Compute enhancement filter string for instant smooth client-side preview
      const master = fe.strength / 100;
      const brightness = (1 + (fe.lighting / 100) * 0.35 * master).toFixed(3);
      const contrast = (1 + (fe.sharpening / 100) * 0.25 * master).toFixed(3);
      const saturate = (1 + master * 0.08).toFixed(3);
      const filterStr = `brightness(${brightness}) contrast(${contrast}) saturate(${saturate})`;

      if (fe.splitCompare) {
        // Left Half: Before (Unenhanced)
        ctx.save();
        ctx.beginPath();
        ctx.rect(0, 0, Math.floor(srcW / 2), srcH);
        ctx.clip();
        ctx.drawImage(baseCanvas, 0, 0);
        ctx.restore();

        // Right Half: After (Enhanced Preview)
        ctx.save();
        ctx.beginPath();
        ctx.rect(Math.floor(srcW / 2), 0, Math.ceil(srcW / 2), srcH);
        ctx.clip();
        ctx.filter = filterStr;
        ctx.drawImage(baseCanvas, 0, 0);
        ctx.restore();

        // Split divider vertical guideline
        ctx.save();
        ctx.strokeStyle = "rgba(255, 255, 255, 0.9)";
        ctx.lineWidth = Math.max(2, Math.round(srcW * 0.003));
        ctx.setLineDash([6, 4]);
        ctx.beginPath();
        ctx.moveTo(Math.floor(srcW / 2), 0);
        ctx.lineTo(Math.floor(srcW / 2), srcH);
        ctx.stroke();
        ctx.restore();
      } else {
        // Full frame enhancement preview
        ctx.save();
        ctx.filter = filterStr;
        ctx.drawImage(baseCanvas, 0, 0);
        ctx.restore();
      }
    }

    // Update Comparison Badge state on preview card
    if (enhancementCompareTag) {
      if (fe.enabled && fe.compareMode) {
        enhancementCompareTag.textContent = "BEFORE";
        enhancementCompareTag.classList.remove("hidden");
      } else if (fe.enabled && fe.splitCompare) {
        enhancementCompareTag.textContent = "SPLIT COMPARE";
        enhancementCompareTag.classList.remove("hidden");
      } else {
        enhancementCompareTag.classList.add("hidden");
      }
    }

    // Telemetry updates
    dbgPreviewRes.textContent = `${srcW} × ${srcH}`;
    dbgExportRes.textContent = `${srcW} × ${srcH} (Full Quality)`;

    // Synchronize 4x6 print sheet composition with real-time passport photo updates
    updatePrintSheetPreview();
  }

  function hexToRgba(hex, opacityPercent = 100) {
    let clean = (hex || "#1877f2").replace("#", "");
    if (clean.length === 3) {
      clean = clean.split("").map((c) => c + c).join("");
    }
    const r = parseInt(clean.substring(0, 2), 16) || 0;
    const g = parseInt(clean.substring(2, 4), 16) || 0;
    const b = parseInt(clean.substring(4, 6), 16) || 0;
    const a = Math.max(0, Math.min(1, opacityPercent / 100));
    return { r, g, b, a, css: `rgba(${r}, ${g}, ${b}, ${a})` };
  }

  function getActiveBgColor() {
    const choice = memoryCache.activeBgChoice;
    if (choice === "white") return "#ffffff";
    if (choice === "blue") return "#1877f2";
    if (choice === "custom") {
      if (memoryCache.activeCustomOpacity < 100) {
        return hexToRgba(memoryCache.activeCustomColor, memoryCache.activeCustomOpacity).css;
      }
      return memoryCache.activeCustomColor;
    }
    return "transparent";
  }

  // --- Step 5: Background Choice Handling ---
  btnKeepOriginalBg.addEventListener("click", () => setBgMode("original"));
  btnRemoveBg.addEventListener("click", () => setBgMode("remove"));

  function setBgMode(mode) {
    memoryCache.bgMode = mode;
    if (mode === "original") {
      btnKeepOriginalBg.classList.add("active");
      btnRemoveBg.classList.remove("active");
      originalBgInfo.classList.remove("hidden");
      removeBgControls.classList.add("hidden");
    } else {
      btnKeepOriginalBg.classList.remove("active");
      btnRemoveBg.classList.add("active");
      originalBgInfo.classList.add("hidden");
      removeBgControls.classList.remove("hidden");

      // If background removal not yet executed for current crop, prompt user or execute
      if (!memoryCache.transparentSubjectImg) {
        runBgBtnText.textContent = "⚡ Run Background Removal on Crop";
      }
    }
    updateLivePassportPreview();
  }

  // Run AI Background Removal on Cropped Person
  runBgRemovalBtn.addEventListener("click", executeCropBackgroundRemoval);

  async function executeCropBackgroundRemoval() {
    if (!memoryCache.sessionId) return;

    runBgRemovalBtn.disabled = true;
    runBgSpinner.classList.remove("hidden");
    runBgBtnText.textContent = "Segmenting Cropped Portrait...";
    showOverlay(true);
    setStage("Running AI background removal on cropped subject...", 50);

    const cn = memoryCache.cropNorm;
    const formData = new FormData();
    formData.append("session_id", memoryCache.sessionId);
    formData.append("crop_x_norm", cn.x);
    formData.append("crop_y_norm", cn.y);
    formData.append("crop_w_norm", cn.w);
    formData.append("crop_h_norm", cn.h);
    formData.append("method_mode", methodModeSelect.value);
    formData.append("smoothness", smoothnessSlider.value);

    try {
      const response = await fetch("/api/photo/process-cropped-background", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Background removal failed.");

      // Load transparent subject image for fast client-side compositing & eraser retouching
      const subjectImg = new Image();
      subjectImg.onload = () => {
        initEraserSubject(subjectImg);
      };
      subjectImg.src = data.previews.transparent_preview;

      // Update Method Banner
      methodLabel.textContent = `Engine: ${data.method_info.selected_method}`;
      methodSub.textContent = data.method_info.reason;
      methodBanner.classList.remove("hidden");

      // Update Telemetry
      dbgSeg.textContent = `${data.timings.segmentation_ms} ms`;
      dbgRefine.textContent = `${data.timings.mask_refinement_ms} ms`;
      debugCard.classList.remove("hidden");

      runBgBtnText.textContent = "✓ Background Removed (Instant Colors Ready)";
    } catch (err) {
      showError(err.message || "Failed to remove background.");
    } finally {
      runBgRemovalBtn.disabled = false;
      runBgSpinner.classList.add("hidden");
      showOverlay(false);
    }
  }

  // --- Background Color Selection (Instant Zero-Lag Compositing) ---
  bgOptions.forEach((item) => {
    item.addEventListener("click", () => {
      bgOptions.forEach((el) => el.classList.remove("active"));
      item.classList.add("active");
      const radio = item.querySelector('input[type="radio"]');
      radio.checked = true;
      memoryCache.activeBgChoice = radio.value;

      if (memoryCache.activeBgChoice === "custom") {
        customColorContainer.classList.remove("hidden");
      } else {
        customColorContainer.classList.add("hidden");
      }

      // If user clicks a studio background color, ensure "Remove Background" mode is active
      if (memoryCache.bgMode !== "remove") {
        setBgMode("remove");
      }

      // If background removal not yet executed, auto-trigger it
      if (!memoryCache.transparentSubjectImg) {
        executeCropBackgroundRemoval();
      } else {
        updateLivePassportPreview();
      }
    });
  });

  colorPickerInput.addEventListener("input", (e) => {
    memoryCache.activeCustomColor = e.target.value;
    colorHexInput.value = memoryCache.activeCustomColor;
    customColorSwatch.style.backgroundColor = hexToRgba(
      memoryCache.activeCustomColor,
      memoryCache.activeCustomOpacity
    ).css;
    if (memoryCache.bgMode === "remove") updateLivePassportPreview();
  });

  colorHexInput.addEventListener("change", (e) => {
    let val = e.target.value.trim();
    if (!val.startsWith("#")) val = "#" + val;
    if (/^#[0-9A-Fa-f]{6}$/.test(val)) {
      memoryCache.activeCustomColor = val;
      colorPickerInput.value = val;
      customColorSwatch.style.backgroundColor = hexToRgba(
        memoryCache.activeCustomColor,
        memoryCache.activeCustomOpacity
      ).css;
      if (memoryCache.bgMode === "remove") updateLivePassportPreview();
    }
  });

  if (colorOpacitySlider) {
    colorOpacitySlider.addEventListener("input", (e) => {
      const val = parseInt(e.target.value, 10);
      memoryCache.activeCustomOpacity = isNaN(val) ? 100 : val;
      if (colorOpacityVal) colorOpacityVal.textContent = `${memoryCache.activeCustomOpacity}%`;
      customColorSwatch.style.backgroundColor = hexToRgba(
        memoryCache.activeCustomColor,
        memoryCache.activeCustomOpacity
      ).css;
      if (memoryCache.bgMode === "remove") updateLivePassportPreview();
    });
  }

  // --- Step 5b: Manual Eraser Retouch Engine ---
  function initEraserSubject(subjectImg) {
    const w = subjectImg.naturalWidth;
    const h = subjectImg.naturalHeight;
    if (!w || !h) return;

    // 1. Offscreen Editable Subject Canvas (Holds transparent cutout)
    const sCanvas = document.createElement("canvas");
    sCanvas.width = w;
    sCanvas.height = h;
    const sCtx = sCanvas.getContext("2d", { willReadFrequently: true });
    sCtx.drawImage(subjectImg, 0, 0, w, h);
    memoryCache.subjectCanvas = sCanvas;
    memoryCache.subjectCtx = sCtx;

    // 2. Pristine AI Cut-out Backup (for Reset)
    const origCanvas = document.createElement("canvas");
    origCanvas.width = w;
    origCanvas.height = h;
    const origCtx = origCanvas.getContext("2d");
    origCtx.drawImage(subjectImg, 0, 0, w, h);
    memoryCache.originalSubjectCanvas = origCanvas;

    // 3. Connect to live passport preview
    memoryCache.transparentSubjectImg = sCanvas;

    // 4. Reset stacks
    memoryCache.undoStack = [];
    memoryCache.redoStack = [];
    memoryCache.maskEdited = false;
    updateUndoRedoButtons();

    updateLivePassportPreview();
  }

  function setEraserActive(active) {
    memoryCache.eraserActive = active;
    if (!btnToggleEraser) return;
    if (active) {
      btnToggleEraser.classList.add("active");
      eraserToggleText.textContent = "Eraser Active";
      eraserControlsBody.classList.remove("hidden");
      eraserToolCard.classList.add("active");
      passportPhotoCard.classList.add("eraser-mode");
    } else {
      btnToggleEraser.classList.remove("active");
      eraserToggleText.textContent = "Enable Eraser";
      eraserControlsBody.classList.add("hidden");
      eraserToolCard.classList.remove("active");
      passportPhotoCard.classList.remove("eraser-mode");
      if (eraserBrushCursor) eraserBrushCursor.classList.add("hidden");
    }
  }

  if (btnToggleEraser) {
    btnToggleEraser.addEventListener("click", () => {
      // If user hasn't removed background yet, trigger it
      if (!memoryCache.transparentSubjectImg) {
        setBgMode("remove");
        executeCropBackgroundRemoval().then(() => {
          setEraserActive(true);
        });
        return;
      }
      setEraserActive(!memoryCache.eraserActive);
    });
  }

  if (eraserSizeSlider) {
    eraserSizeSlider.addEventListener("input", (e) => {
      memoryCache.eraserSize = parseInt(e.target.value, 10);
      eraserSizeVal.textContent = `${memoryCache.eraserSize} px`;
    });
  }

  if (eraserHardnessSlider) {
    eraserHardnessSlider.addEventListener("input", (e) => {
      const pct = parseInt(e.target.value, 10);
      memoryCache.eraserHardness = pct / 100;
      let label = `${pct}%`;
      if (pct <= 25) label = `Soft (${pct}%)`;
      else if (pct >= 85) label = `Hard (${pct}%)`;
      else label = `Medium (${pct}%)`;
      eraserHardnessVal.textContent = label;
    });
  }

  function createBrushStamp(radius, hardness) {
    const stampCanvas = document.createElement("canvas");
    const d = Math.max(2, Math.round(radius * 2));
    stampCanvas.width = d;
    stampCanvas.height = d;
    const sCtx = stampCanvas.getContext("2d");

    if (hardness >= 0.95) {
      sCtx.fillStyle = "#000000";
      sCtx.beginPath();
      sCtx.arc(radius, radius, radius, 0, Math.PI * 2);
      sCtx.fill();
    } else {
      const grad = sCtx.createRadialGradient(radius, radius, radius * hardness, radius, radius, radius);
      grad.addColorStop(0, "rgba(0, 0, 0, 1)");
      grad.addColorStop(1, "rgba(0, 0, 0, 0)");
      sCtx.fillStyle = grad;
      sCtx.beginPath();
      sCtx.arc(radius, radius, radius, 0, Math.PI * 2);
      sCtx.fill();
    }
    return stampCanvas;
  }

  function eraseAtPoint(x, y, radius, hardness) {
    if (!memoryCache.subjectCtx) return;
    const stamp = createBrushStamp(radius, hardness);
    const sCtx = memoryCache.subjectCtx;
    sCtx.globalCompositeOperation = "destination-out";
    sCtx.drawImage(stamp, Math.round(x - radius), Math.round(y - radius));
    sCtx.globalCompositeOperation = "source-over";
  }

  function eraseLine(x0, y0, x1, y1, radius, hardness) {
    const dist = Math.hypot(x1 - x0, y1 - y0);
    const step = Math.max(1, radius * 0.25);
    if (dist < 1) {
      eraseAtPoint(x1, y1, radius, hardness);
      return;
    }
    for (let t = 0; t <= dist; t += step) {
      const x = x0 + (x1 - x0) * (t / dist);
      const y = y0 + (y1 - y0) * (t / dist);
      eraseAtPoint(x, y, radius, hardness);
    }
    eraseAtPoint(x1, y1, radius, hardness);
  }

  function getCanvasCoord(e) {
    const rect = passportPreviewCanvas.getBoundingClientRect();
    const targetW = memoryCache.subjectCanvas ? memoryCache.subjectCanvas.width : passportPreviewCanvas.width;
    const targetH = memoryCache.subjectCanvas ? memoryCache.subjectCanvas.height : passportPreviewCanvas.height;
    const scaleX = targetW / rect.width;
    const scaleY = targetH / rect.height;
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY,
      cssX: e.clientX - rect.left,
      cssY: e.clientY - rect.top,
      cssScale: rect.width / targetW
    };
  }

  const MAX_UNDO = 20;

  function pushUndoState() {
    if (!memoryCache.subjectCtx) return;
    const w = memoryCache.subjectCanvas.width;
    const h = memoryCache.subjectCanvas.height;
    const snapshot = memoryCache.subjectCtx.getImageData(0, 0, w, h);
    memoryCache.undoStack.push(snapshot);
    if (memoryCache.undoStack.length > MAX_UNDO) {
      memoryCache.undoStack.shift();
    }
    memoryCache.redoStack = [];
    updateUndoRedoButtons();
  }

  function performUndo() {
    if (!memoryCache.subjectCtx || memoryCache.undoStack.length === 0) return;
    const w = memoryCache.subjectCanvas.width;
    const h = memoryCache.subjectCanvas.height;
    const current = memoryCache.subjectCtx.getImageData(0, 0, w, h);
    memoryCache.redoStack.push(current);

    const prev = memoryCache.undoStack.pop();
    memoryCache.subjectCtx.putImageData(prev, 0, 0);
    memoryCache.maskEdited = true;
    updateUndoRedoButtons();
    updateLivePassportPreview();
  }

  function performRedo() {
    if (!memoryCache.subjectCtx || memoryCache.redoStack.length === 0) return;
    const w = memoryCache.subjectCanvas.width;
    const h = memoryCache.subjectCanvas.height;
    const current = memoryCache.subjectCtx.getImageData(0, 0, w, h);
    memoryCache.undoStack.push(current);

    const next = memoryCache.redoStack.pop();
    memoryCache.subjectCtx.putImageData(next, 0, 0);
    memoryCache.maskEdited = true;
    updateUndoRedoButtons();
    updateLivePassportPreview();
  }

  function performResetMask() {
    if (!memoryCache.subjectCtx || !memoryCache.originalSubjectCanvas) return;
    pushUndoState();
    const w = memoryCache.subjectCanvas.width;
    const h = memoryCache.subjectCanvas.height;
    memoryCache.subjectCtx.clearRect(0, 0, w, h);
    memoryCache.subjectCtx.globalCompositeOperation = "source-over";
    memoryCache.subjectCtx.drawImage(memoryCache.originalSubjectCanvas, 0, 0, w, h);
    memoryCache.maskEdited = false;
    updateUndoRedoButtons();
    updateLivePassportPreview();
  }

  function updateUndoRedoButtons() {
    if (btnEraserUndo) btnEraserUndo.disabled = memoryCache.undoStack.length === 0;
    if (btnEraserRedo) btnEraserRedo.disabled = memoryCache.redoStack.length === 0;
  }

  if (btnEraserUndo) btnEraserUndo.addEventListener("click", performUndo);
  if (btnEraserRedo) btnEraserRedo.addEventListener("click", performRedo);
  if (btnEraserReset) btnEraserReset.addEventListener("click", performResetMask);

  // Keyboard shortcuts (Ctrl+Z / Ctrl+Y / Ctrl+Shift+Z)
  window.addEventListener("keydown", (e) => {
    if (!memoryCache.eraserActive) return;
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z") {
      e.preventDefault();
      if (e.shiftKey) {
        performRedo();
      } else {
        performUndo();
      }
    } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "y") {
      e.preventDefault();
      performRedo();
    }
  });

  // Convert subject canvas alpha to mask data URL for full-res export
  function getMaskDataUrl(subjectCanvas) {
    if (!subjectCanvas) return null;
    const w = subjectCanvas.width;
    const h = subjectCanvas.height;
    const ctx = subjectCanvas.getContext("2d");
    const imgData = ctx.getImageData(0, 0, w, h);
    const data = imgData.data;

    const mCanvas = document.createElement("canvas");
    mCanvas.width = w;
    mCanvas.height = h;
    const mCtx = mCanvas.getContext("2d");
    const mImgData = mCtx.createImageData(w, h);
    const mData = mImgData.data;

    for (let i = 0; i < data.length; i += 4) {
      const a = data[i + 3];
      mData[i] = a;
      mData[i + 1] = a;
      mData[i + 2] = a;
      mData[i + 3] = 255;
    }
    mCtx.putImageData(mImgData, 0, 0);
    return mCanvas.toDataURL("image/png");
  }

  // Pointer drawing on passportPreviewCanvas
  if (passportPreviewCanvas) {
    passportPreviewCanvas.addEventListener("pointerdown", (e) => {
      if (!memoryCache.eraserActive || !memoryCache.subjectCanvas) return;
      e.preventDefault();
      try {
        passportPreviewCanvas.setPointerCapture(e.pointerId);
      } catch (err) {}

      pushUndoState();
      memoryCache.isErasing = true;
      const coord = getCanvasCoord(e);
      eraseAtPoint(coord.x, coord.y, memoryCache.eraserSize, memoryCache.eraserHardness);
      memoryCache.lastEraserPoint = { x: coord.x, y: coord.y };
      memoryCache.maskEdited = true;
      updateLivePassportPreview();
    });

    passportPreviewCanvas.addEventListener("pointermove", (e) => {
      const coord = getCanvasCoord(e);

      // Update brush ring cursor
      if (memoryCache.eraserActive && eraserBrushCursor) {
        const radiusCss = memoryCache.eraserSize * coord.cssScale;
        const diamCss = Math.max(4, Math.round(radiusCss * 2));
        eraserBrushCursor.style.width = `${diamCss}px`;
        eraserBrushCursor.style.height = `${diamCss}px`;
        eraserBrushCursor.style.left = `${Math.round(coord.cssX)}px`;
        eraserBrushCursor.style.top = `${Math.round(coord.cssY)}px`;
        eraserBrushCursor.classList.remove("hidden");
      }

      if (!memoryCache.isErasing || !memoryCache.eraserActive || !memoryCache.subjectCanvas) return;
      e.preventDefault();

      eraseLine(
        memoryCache.lastEraserPoint.x,
        memoryCache.lastEraserPoint.y,
        coord.x,
        coord.y,
        memoryCache.eraserSize,
        memoryCache.eraserHardness
      );
      memoryCache.lastEraserPoint = { x: coord.x, y: coord.y };
      memoryCache.maskEdited = true;
      updateLivePassportPreview();
    });

    const stopErasing = (e) => {
      if (memoryCache.isErasing) {
        memoryCache.isErasing = false;
        memoryCache.lastEraserPoint = null;
        try {
          passportPreviewCanvas.releasePointerCapture(e.pointerId);
        } catch (err) {}
      }
    };

    passportPreviewCanvas.addEventListener("pointerup", stopErasing);
    passportPreviewCanvas.addEventListener("pointercancel", stopErasing);
    passportPreviewCanvas.addEventListener("pointerleave", () => {
      if (eraserBrushCursor) eraserBrushCursor.classList.add("hidden");
    });
    passportPreviewCanvas.addEventListener("pointerenter", () => {
      if (memoryCache.eraserActive && eraserBrushCursor) {
        eraserBrushCursor.classList.remove("hidden");
      }
    });
  }

  // --- Step 6: Face Enhancement Controls & Preview Architecture ---
  const ENHANCEMENT_PRESETS = {
    natural: { strength: 40, lighting: 5, smoothing: 25, blemish: 20, sharpening: 15 },
    studio: { strength: 65, lighting: 15, smoothing: 50, blemish: 40, sharpening: 25 },
    crisp: { strength: 75, lighting: 10, smoothing: 30, blemish: 30, sharpening: 50 },
    reset: { strength: 50, lighting: 10, smoothing: 35, blemish: 25, sharpening: 20 }
  };

  if (toggleEnhancement) {
    toggleEnhancement.addEventListener("change", (e) => {
      const isEnabled = e.target.checked;
      memoryCache.faceEnhancement.enabled = isEnabled;
      if (isEnabled) {
        enhancementBody.classList.remove("disabled-panel");
        enhancementStatusLabel.textContent = "Enhancement Active";
      } else {
        enhancementBody.classList.add("disabled-panel");
        enhancementStatusLabel.textContent = "Enhancement Disabled";
        memoryCache.faceEnhancement.compareMode = false;
        memoryCache.faceEnhancement.splitCompare = false;
        if (btnCompareToggle) btnCompareToggle.classList.remove("active");
        if (btnCompareHold) btnCompareHold.classList.remove("active");
      }
      updateLivePassportPreview();
    });
  }

  // Slider event listeners for instant, smooth client-side preview
  if (enhancementStrengthSlider) {
    enhancementStrengthSlider.addEventListener("input", (e) => {
      const val = parseInt(e.target.value, 10);
      memoryCache.faceEnhancement.strength = val;
      if (enhancementStrengthVal) enhancementStrengthVal.textContent = `${val}%`;
      updateLivePassportPreview();
    });
  }

  if (enhancementLightingSlider) {
    enhancementLightingSlider.addEventListener("input", (e) => {
      const val = parseInt(e.target.value, 10);
      memoryCache.faceEnhancement.lighting = val;
      if (enhancementLightingVal) enhancementLightingVal.textContent = `${val > 0 ? "+" : ""}${val}%`;
      updateLivePassportPreview();
    });
  }

  if (enhancementSmoothingSlider) {
    enhancementSmoothingSlider.addEventListener("input", (e) => {
      const val = parseInt(e.target.value, 10);
      memoryCache.faceEnhancement.smoothing = val;
      if (enhancementSmoothingVal) enhancementSmoothingVal.textContent = `${val}%`;
      updateLivePassportPreview();
    });
  }

  if (enhancementBlemishSlider) {
    enhancementBlemishSlider.addEventListener("input", (e) => {
      const val = parseInt(e.target.value, 10);
      memoryCache.faceEnhancement.blemish = val;
      if (enhancementBlemishVal) enhancementBlemishVal.textContent = `${val}%`;
      updateLivePassportPreview();
    });
  }

  if (enhancementSharpeningSlider) {
    enhancementSharpeningSlider.addEventListener("input", (e) => {
      const val = parseInt(e.target.value, 10);
      memoryCache.faceEnhancement.sharpening = val;
      if (enhancementSharpeningVal) enhancementSharpeningVal.textContent = `${val}%`;
      updateLivePassportPreview();
    });
  }

  // Preset Buttons
  function applyEnhancementPreset(params) {
    if (!params) return;
    memoryCache.faceEnhancement.strength = params.strength;
    memoryCache.faceEnhancement.lighting = params.lighting;
    memoryCache.faceEnhancement.smoothing = params.smoothing;
    memoryCache.faceEnhancement.blemish = params.blemish;
    memoryCache.faceEnhancement.sharpening = params.sharpening;

    if (enhancementStrengthSlider) {
      enhancementStrengthSlider.value = params.strength;
      if (enhancementStrengthVal) enhancementStrengthVal.textContent = `${params.strength}%`;
    }
    if (enhancementLightingSlider) {
      enhancementLightingSlider.value = params.lighting;
      if (enhancementLightingVal) enhancementLightingVal.textContent = `${params.lighting > 0 ? "+" : ""}${params.lighting}%`;
    }
    if (enhancementSmoothingSlider) {
      enhancementSmoothingSlider.value = params.smoothing;
      if (enhancementSmoothingVal) enhancementSmoothingVal.textContent = `${params.smoothing}%`;
    }
    if (enhancementBlemishSlider) {
      enhancementBlemishSlider.value = params.blemish;
      if (enhancementBlemishVal) enhancementBlemishVal.textContent = `${params.blemish}%`;
    }
    if (enhancementSharpeningSlider) {
      enhancementSharpeningSlider.value = params.sharpening;
      if (enhancementSharpeningVal) enhancementSharpeningVal.textContent = `${params.sharpening}%`;
    }
    updateLivePassportPreview();
  }

  presetBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const pKey = btn.getAttribute("data-preset");
      if (ENHANCEMENT_PRESETS[pKey]) {
        applyEnhancementPreset(ENHANCEMENT_PRESETS[pKey]);
      }
    });
  });

  if (btnResetEnhancement) {
    btnResetEnhancement.addEventListener("click", () => {
      applyEnhancementPreset(ENHANCEMENT_PRESETS.reset);
    });
  }

  // Before / After Compare Controls
  if (btnCompareHold) {
    const startCompare = (e) => {
      if (!memoryCache.faceEnhancement.enabled) return;
      e.preventDefault();
      memoryCache.faceEnhancement.compareMode = true;
      btnCompareHold.classList.add("active");
      updateLivePassportPreview();
    };
    const endCompare = (e) => {
      if (!memoryCache.faceEnhancement.compareMode) return;
      e.preventDefault();
      memoryCache.faceEnhancement.compareMode = false;
      btnCompareHold.classList.remove("active");
      updateLivePassportPreview();
    };

    btnCompareHold.addEventListener("pointerdown", startCompare);
    btnCompareHold.addEventListener("pointerup", endCompare);
    btnCompareHold.addEventListener("pointercancel", endCompare);
    btnCompareHold.addEventListener("mouseleave", endCompare);
  }

  if (btnCompareToggle) {
    btnCompareToggle.addEventListener("click", () => {
      if (!memoryCache.faceEnhancement.enabled) return;
      memoryCache.faceEnhancement.splitCompare = !memoryCache.faceEnhancement.splitCompare;
      btnCompareToggle.classList.toggle("active", memoryCache.faceEnhancement.splitCompare);
      updateLivePassportPreview();
    });
  }

  // --- Step 7: Full Resolution Download / Export ---
  [downloadBtn, downloadPanelBtn].forEach((btn) => {
    if (!btn) return;
    btn.addEventListener("click", async () => {
      if (!memoryCache.sessionId) return;

      btn.classList.add("disabled");
      downloadSpinner.classList.remove("hidden");
      downloadIcon.classList.add("hidden");
      downloadBtnText.textContent = "Exporting Full Res...";

      const t0 = performance.now();
      const cn = memoryCache.cropNorm;
      const formData = new FormData();
      formData.append("session_id", memoryCache.sessionId);
      formData.append("bg_type", memoryCache.bgMode === "original" ? "original" : memoryCache.activeBgChoice);
      if (memoryCache.bgMode === "remove" && memoryCache.activeBgChoice === "custom") {
        const opacityHex = Math.round((memoryCache.activeCustomOpacity / 100) * 255)
          .toString(16)
          .padStart(2, "0");
        formData.append("custom_color", memoryCache.activeCustomColor + opacityHex);
      }
      formData.append("crop_x_norm", cn.x);
      formData.append("crop_y_norm", cn.y);
      formData.append("crop_w_norm", cn.w);
      formData.append("crop_h_norm", cn.h);

      // Pass user-edited mask if manual eraser was used
      if (memoryCache.bgMode === "remove" && memoryCache.maskEdited && memoryCache.subjectCanvas) {
        const maskUrl = getMaskDataUrl(memoryCache.subjectCanvas);
        if (maskUrl) formData.append("edited_mask", maskUrl);
      }

      try {
        const resp = await fetch("/api/photo/export-final", {
          method: "POST",
          body: formData,
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || "Full resolution export failed.");

        const exportMs = Math.round(performance.now() - t0);
        dbgExport.textContent = `${exportMs} ms (${data.export_time_ms} ms server)`;

        // Trigger native download
        const tempLink = document.createElement("a");
        tempLink.href = data.download_url;
        const bgSuffix = memoryCache.bgMode === "original" ? "original" : memoryCache.activeBgChoice;
        tempLink.setAttribute("download", `passport_${memoryCache.activeRatioName.replace(":", "x")}_${bgSuffix}.png`);
        document.body.appendChild(tempLink);
        tempLink.click();
        document.body.removeChild(tempLink);
      } catch (err) {
        showError(err.message || "Failed to export passport photo.");
      } finally {
        btn.classList.remove("disabled");
        downloadSpinner.classList.add("hidden");
        downloadIcon.classList.remove("hidden");
        downloadBtnText.textContent = "Download Full Res";
      }
    });
  });

  // --- Step 8: Print-Ready 4x6 Layout Logic & Live Composition ---
  function calculatePrintGrid(sheetW, sheetH, margin, spacing, aspect) {
    let best = null;
    for (let c = 1; c <= 5; c++) {
      for (let r = 1; r <= 6; r++) {
        const availW = sheetW - 2 * margin - (c - 1) * spacing;
        const availH = sheetH - 2 * margin - (r - 1) * spacing;
        if (availW <= 0 || availH <= 0) continue;

        const slotW = availW / c;
        const slotH = availH / r;

        let photoW, photoH;
        if (slotW / slotH > aspect) {
          photoH = slotH;
          photoW = photoH * aspect;
        } else {
          photoW = slotW;
          photoH = photoW / aspect;
        }

        const count = c * r;
        if (aspect >= 0.95 && count > 6) continue;
        if (count > 8) continue;

        if (!best || count > best.count || (count === best.count && (photoW * photoH) > (best.photoW * best.photoH))) {
          best = {
            cols: c,
            rows: r,
            count: count,
            photoW: Math.round(photoW),
            photoH: Math.round(photoH)
          };
        }
      }
    }
    return best || { cols: 2, rows: 4, count: 8, photoW: 320, photoH: 411 };
  }

  function updatePrintSheetPreview() {
    if (!printSheetCanvas) return;

    const pl = memoryCache.printLayout;
    const isPortrait = pl.orientation === "portrait";
    const sheetW = isPortrait ? 1200 : 1800;
    const sheetH = isPortrait ? 1800 : 1200;

    // Buffer dimensions: exact 1200x1800 or 1800x1200 (True 300 DPI canvas)
    if (printSheetCanvas.width !== sheetW || printSheetCanvas.height !== sheetH) {
      printSheetCanvas.width = sheetW;
      printSheetCanvas.height = sheetH;
    }

    const ctx = printSheetCanvas.getContext("2d");
    // Crisp photo paper pure white background
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, sheetW, sheetH);

    // Compute grid using exact passport photo aspect ratio
    const passportAspect = (passportPreviewCanvas && passportPreviewCanvas.height > 0)
      ? (passportPreviewCanvas.width / passportPreviewCanvas.height)
      : (memoryCache.activeRatioVal || (35.0 / 45.0));
    const grid = calculatePrintGrid(sheetW, sheetH, pl.marginPx, pl.spacingPx, passportAspect);
    pl.cols = grid.cols;
    pl.rows = grid.rows;
    pl.maxFit = grid.count;

    // Clamp copies
    if (pl.copies > pl.maxFit) pl.copies = pl.maxFit;
    if (pl.copies < 1) pl.copies = 1;

    // Update UI elements
    if (printCopiesInput) printCopiesInput.value = pl.copies;
    if (printCopiesVal) printCopiesVal.textContent = `${pl.copies} ${pl.copies === 1 ? "copy" : "copies"}`;
    if (printGridLabel) printGridLabel.textContent = `${grid.cols} cols × ${grid.rows} rows (${grid.count} max fit)`;
    if (printRatioLabel) printRatioLabel.textContent = `${memoryCache.activeRatioName} (Aspect Locked)`;
    if (sheetDimTag) sheetDimTag.textContent = `${isPortrait ? "Portrait 4 × 6 in (1200 × 1800 px)" : "Landscape 6 × 4 in (1800 × 1200 px)"} • 300 DPI`;

    // Scale printSheetPaperCard and printSheetCanvas to strictly fit the available viewport with exact page aspect ratio (zero distortion)
    if (printSheetPaperCard && printSheetCanvas) {
      printSheetPaperCard.classList.toggle("landscape-sheet", !isPortrait);
      const container = printSheetCanvasArea || printSheetPaperCard.parentElement;
      if (container) {
        const computed = window.getComputedStyle(container);
        const padX = (parseFloat(computed.paddingLeft) || 0) + (parseFloat(computed.paddingRight) || 0);
        const padY = (parseFloat(computed.paddingTop) || 0) + (parseFloat(computed.paddingBottom) || 0);
        const availW = Math.max(100, Math.floor(container.clientWidth - padX - 16));
        const availH = Math.max(100, Math.floor(container.clientHeight - padY - 16));
        const sheetAspect = sheetW / sheetH; // Strictly 1.5 in landscape (1800/1200), 0.66667 in portrait (1200/1800)

        let targetW, targetH;
        if (availW / availH > sheetAspect) {
          targetH = availH;
          targetW = Math.round(targetH * sheetAspect);
        } else {
          targetW = availW;
          targetH = Math.round(targetW / sheetAspect);
        }

        printSheetCanvas.style.width = `${targetW}px`;
        printSheetCanvas.style.height = `${targetH}px`;
        printSheetPaperCard.style.width = `${targetW}px`;
        printSheetPaperCard.style.height = `${targetH}px`;
      }
    }

    // Centered grid coordinates
    const totalW = grid.cols * grid.photoW + (grid.cols - 1) * pl.spacingPx;
    const totalH = grid.rows * grid.photoH + (grid.rows - 1) * pl.spacingPx;
    const startX = Math.round((sheetW - totalW) / 2);
    const startY = Math.round((sheetH - totalH) / 2);

    // Subtle sheet margin boundary line
    ctx.save();
    ctx.strokeStyle = "rgba(226, 232, 240, 0.7)";
    ctx.lineWidth = 1;
    ctx.strokeRect(pl.marginPx, pl.marginPx, sheetW - 2 * pl.marginPx, sheetH - 2 * pl.marginPx);
    ctx.restore();

    // Source photo: the live finalized passport canvas
    const hasPhoto = passportPreviewCanvas && passportPreviewCanvas.width > 0 && memoryCache.currentFile;

    // Draw slots
    for (let idx = 0; idx < grid.count; idx++) {
      const r = Math.floor(idx / grid.cols);
      const c = idx % grid.cols;
      const px = startX + c * (grid.photoW + pl.spacingPx);
      const py = startY + r * (grid.photoH + pl.spacingPx);

      if (idx < pl.copies) {
        if (hasPhoto) {
          ctx.drawImage(passportPreviewCanvas, px, py, grid.photoW, grid.photoH);
        } else {
          ctx.fillStyle = "#f1f5f9";
          ctx.fillRect(px, py, grid.photoW, grid.photoH);
        }

        // Clean solid BLACK cutting border around every passport photo
        if (pl.borderPx > 0) {
          ctx.save();
          ctx.strokeStyle = "#000000";
          ctx.lineWidth = pl.borderPx;
          const halfB = pl.borderPx / 2;
          ctx.strokeRect(px + halfB, py + halfB, grid.photoW - pl.borderPx, grid.photoH - pl.borderPx);
          ctx.restore();
        }
      } else {
        // Empty slot guide outline
        ctx.save();
        ctx.strokeStyle = "rgba(203, 213, 225, 0.6)";
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);
        ctx.strokeRect(px, py, grid.photoW, grid.photoH);
        ctx.restore();
      }
    }
  }

  // --- Step 8 Controls Event Handlers ---
  if (btnOrientPortrait) {
    btnOrientPortrait.addEventListener("click", () => {
      memoryCache.printLayout.orientation = "portrait";
      btnOrientPortrait.classList.add("active");
      if (btnOrientLandscape) btnOrientLandscape.classList.remove("active");
      updatePrintSheetPreview();
    });
  }

  if (btnOrientLandscape) {
    btnOrientLandscape.addEventListener("click", () => {
      memoryCache.printLayout.orientation = "landscape";
      btnOrientLandscape.classList.add("active");
      if (btnOrientPortrait) btnOrientPortrait.classList.remove("active");
      updatePrintSheetPreview();
    });
  }

  if (printCopiesInput) {
    printCopiesInput.addEventListener("input", (e) => {
      let val = parseInt(e.target.value, 10);
      if (isNaN(val)) val = 1;
      val = Math.max(1, Math.min(val, memoryCache.printLayout.maxFit));
      memoryCache.printLayout.copies = val;
      updatePrintSheetPreview();
    });
  }

  if (btnCopiesMinus) {
    btnCopiesMinus.addEventListener("click", () => {
      if (memoryCache.printLayout.copies > 1) {
        memoryCache.printLayout.copies--;
        updatePrintSheetPreview();
      }
    });
  }

  if (btnCopiesPlus) {
    btnCopiesPlus.addEventListener("click", () => {
      if (memoryCache.printLayout.copies < memoryCache.printLayout.maxFit) {
        memoryCache.printLayout.copies++;
        updatePrintSheetPreview();
      }
    });
  }

  if (btnMaxFit) {
    btnMaxFit.addEventListener("click", () => {
      memoryCache.printLayout.copies = memoryCache.printLayout.maxFit;
      updatePrintSheetPreview();
    });
  }

  if (printBorderSlider) {
    printBorderSlider.addEventListener("input", (e) => {
      const val = parseInt(e.target.value, 10);
      memoryCache.printLayout.borderPx = val;
      if (printBorderVal) printBorderVal.textContent = `${val} px`;
      updatePrintSheetPreview();
    });
  }

  if (printSpacingSlider) {
    printSpacingSlider.addEventListener("input", (e) => {
      const val = parseInt(e.target.value, 10);
      memoryCache.printLayout.spacingPx = val;
      if (printSpacingVal) printSpacingVal.textContent = `${val} px`;
      updatePrintSheetPreview();
    });
  }

  if (printMarginSlider) {
    printMarginSlider.addEventListener("input", (e) => {
      const val = parseInt(e.target.value, 10);
      memoryCache.printLayout.marginPx = val;
      if (printMarginVal) printMarginVal.textContent = `${val} px`;
      updatePrintSheetPreview();
    });
  }

  // Download 4x6 Sheet Button Handler
  if (btnDownload4x6) {
    btnDownload4x6.addEventListener("click", async () => {
      if (!memoryCache.sessionId && (!passportPreviewCanvas || passportPreviewCanvas.width === 0)) return;

      btnDownload4x6.classList.add("disabled");
      if (download4x6Spinner) download4x6Spinner.classList.remove("hidden");
      if (download4x6BtnText) download4x6BtnText.textContent = "Compositing 300 DPI Sheet...";

      const pl = memoryCache.printLayout;
      const cn = memoryCache.cropNorm;

      try {
        let downloaded = false;

        // Try server high-res 300 DPI export
        if (memoryCache.sessionId) {
          try {
            const formData = new FormData();
            formData.append("session_id", memoryCache.sessionId);
            formData.append("copies", pl.copies);
            formData.append("orientation", pl.orientation);
            formData.append("border_px", pl.borderPx);
            formData.append("spacing_px", pl.spacingPx);
            formData.append("margin_px", pl.marginPx);
            formData.append("bg_type", memoryCache.bgMode === "original" ? "original" : memoryCache.activeBgChoice);
            if (memoryCache.bgMode === "remove" && memoryCache.activeBgChoice === "custom") {
              const opacityHex = Math.round((memoryCache.activeCustomOpacity / 100) * 255)
                .toString(16)
                .padStart(2, "0");
              formData.append("custom_color", memoryCache.activeCustomColor + opacityHex);
            }
            formData.append("crop_x_norm", cn.x);
            formData.append("crop_y_norm", cn.y);
            formData.append("crop_w_norm", cn.w);
            formData.append("crop_h_norm", cn.h);
            if (memoryCache.bgMode === "remove" && memoryCache.maskEdited && memoryCache.subjectCanvas) {
              const maskUrl = getMaskDataUrl(memoryCache.subjectCanvas);
              if (maskUrl) formData.append("edited_mask", maskUrl);
            }

            const resp = await fetch("/api/photo/export-4x6", {
              method: "POST",
              body: formData,
            });
            const data = await resp.json();
            if (resp.ok && data.download_url) {
              const tempLink = document.createElement("a");
              tempLink.href = data.download_url;
              tempLink.setAttribute("download", `snap2print_4x6_${pl.orientation}_${pl.copies}copies.png`);
              document.body.appendChild(tempLink);
              tempLink.click();
              document.body.removeChild(tempLink);
              downloaded = true;
            }
          } catch (serverErr) {
            console.warn("Server 4x6 export failed, falling back to client 300 DPI canvas export:", serverErr);
          }
        }

        // Fast client-side 300 DPI canvas export fallback if server didn't complete
        if (!downloaded && printSheetCanvas) {
          updatePrintSheetPreview();
          await new Promise((resolve, reject) => {
            printSheetCanvas.toBlob((blob) => {
              if (!blob) {
                reject(new Error("Canvas export failed"));
                return;
              }
              const url = URL.createObjectURL(blob);
              const tempLink = document.createElement("a");
              tempLink.href = url;
              tempLink.setAttribute("download", `snap2print_4x6_${pl.orientation}_${pl.copies}copies.png`);
              document.body.appendChild(tempLink);
              tempLink.click();
              document.body.removeChild(tempLink);
              URL.revokeObjectURL(url);
              resolve();
            }, "image/png");
          });
        }
      } catch (err) {
        showError(err.message || "Failed to export 4x6 print sheet.");
      } finally {
        btnDownload4x6.classList.remove("disabled");
        if (download4x6Spinner) download4x6Spinner.classList.add("hidden");
        if (download4x6BtnText) download4x6BtnText.textContent = "Download 4×6 Print Sheet (300 DPI)";
      }
    });
  }

  // --- Render Face Overlay Boxes on Original Image ---
  function updateFaceOverlays() {
    faceOverlaysContainer.innerHTML = "";
    const fd = memoryCache.faceDetection;
    if (!fd || !fd.detected) return;

    const rect = getRenderedImageRect();
    if (!rect) return;

    const faces = fd.faces || [];
    faces.forEach((face) => {
      const bbox = face.bounding_box;
      if (!bbox) return;

      const boxX = rect.offsetX + bbox.x_norm * rect.renderedW;
      const boxY = rect.offsetY + bbox.y_norm * rect.renderedH;
      const boxW = bbox.w_norm * rect.renderedW;
      const boxH = bbox.h_norm * rect.renderedH;

      const boxDiv = document.createElement("div");
      boxDiv.className = `face-box-overlay ${face.id === memoryCache.selectedFaceId ? "selected" : ""}`;
      boxDiv.setAttribute("data-face-id", face.id);
      boxDiv.style.left = `${Math.round(boxX)}px`;
      boxDiv.style.top = `${Math.round(boxY)}px`;
      boxDiv.style.width = `${Math.round(boxW)}px`;
      boxDiv.style.height = `${Math.round(boxH)}px`;

      const tagSpan = document.createElement("span");
      tagSpan.className = "face-box-tag";
      tagSpan.textContent = `${face.label || `Face ${face.id}`}`;
      boxDiv.appendChild(tagSpan);

      boxDiv.addEventListener("click", (e) => {
        e.stopPropagation();
        selectPerson(face.id);
      });

      faceOverlaysContainer.appendChild(boxDiv);

      if (face.landmarks) {
        ["right_eye", "left_eye", "nose_tip", "right_mouth", "left_mouth"].forEach((k) => {
          const pt = face.landmarks[k];
          if (pt) {
            const ptX = rect.offsetX + pt.x_norm * rect.renderedW;
            const ptY = rect.offsetY + pt.y_norm * rect.renderedH;
            const dot = document.createElement("div");
            dot.className = "face-landmark-dot";
            dot.style.left = `${Math.round(ptX)}px`;
            dot.style.top = `${Math.round(ptY)}px`;
            faceOverlaysContainer.appendChild(dot);
          }
        });
      }
    });
  }

  // --- View Mode Tabs ---
  tabOriginal.addEventListener("click", () => setViewMode("original"));
  tabProcessed.addEventListener("click", () => setViewMode("processed"));
  tabSplit.addEventListener("click", () => setViewMode("split"));
  if (tabPrint) tabPrint.addEventListener("click", () => setViewMode("print"));
  if (btnSwitchToPassport) btnSwitchToPassport.addEventListener("click", () => setViewMode("processed"));

  function setViewMode(mode) {
    memoryCache.currentViewMode = mode;
    [tabOriginal, tabProcessed, tabSplit, tabPrint].forEach((b) => b && b.classList.remove("active"));
    dualPanelContainer.classList.remove("single-mode-original", "single-mode-processed");

    if (mode === "print") {
      if (tabPrint) tabPrint.classList.add("active");
      dualPanelContainer.classList.add("hidden");
      if (printViewportContainer) printViewportContainer.classList.remove("hidden");
      updatePrintSheetPreview();
      setTimeout(updatePrintSheetPreview, 40);
    } else {
      dualPanelContainer.classList.remove("hidden");
      if (printViewportContainer) printViewportContainer.classList.add("hidden");

      if (mode === "original") {
        tabOriginal.classList.add("active");
        dualPanelContainer.classList.add("single-mode-original");
      } else if (mode === "processed") {
        tabProcessed.classList.add("active");
        dualPanelContainer.classList.add("single-mode-processed");
      } else {
        tabSplit.classList.add("active");
      }

      setTimeout(() => {
        updateCropBoxDOM();
        updateFaceOverlays();
        updateLivePassportPreview();
      }, 40);
    }
  }

  // --- Reset Entire Workspace ---
  function resetState() {
    memoryCache.currentFile = null;
    memoryCache.sessionId = null;
    memoryCache.faceDetection = null;
    memoryCache.selectedFaceId = null;
    memoryCache.transparentSubjectImg = null;
    memoryCache.bgMode = "original";
    memoryCache.activeCustomOpacity = 100;
    if (colorOpacitySlider) colorOpacitySlider.value = 100;
    if (colorOpacityVal) colorOpacityVal.textContent = "100%";

    // Reset eraser state
    setEraserActive(false);
    memoryCache.maskEdited = false;
    memoryCache.undoStack = [];
    memoryCache.redoStack = [];
    memoryCache.subjectCanvas = null;
    memoryCache.subjectCtx = null;
    memoryCache.originalSubjectCanvas = null;

    fileInput.value = "";
    fileInfoBar.classList.add("hidden");
    dropzoneContent.classList.remove("hidden");
    personSelectCard.classList.add("hidden");
    cropControlsCard.classList.add("hidden");
    backgroundChoiceCard.classList.add("hidden");
    if (faceEnhancementCard) faceEnhancementCard.classList.add("hidden");
    exportCard.classList.add("hidden");
    if (printLayoutCard) printLayoutCard.classList.add("hidden");
    if (printViewportContainer) printViewportContainer.classList.add("hidden");
    methodBanner.classList.add("hidden");
    debugCard.classList.add("hidden");
    downloadBtn.classList.add("disabled");

    // Reset 4x6 print layout state
    if (tabPrint) tabPrint.classList.remove("active");
    if (btnOrientPortrait) btnOrientPortrait.classList.add("active");
    if (btnOrientLandscape) btnOrientLandscape.classList.remove("active");
    if (printBorderSlider) printBorderSlider.value = 2;
    if (printBorderVal) printBorderVal.textContent = "2 px";
    if (printSpacingSlider) printSpacingSlider.value = 20;
    if (printSpacingVal) printSpacingVal.textContent = "20 px";
    if (printMarginSlider) printMarginSlider.value = 30;
    if (printMarginVal) printMarginVal.textContent = "30 px";
    if (printCopiesInput) printCopiesInput.value = 8;
    if (printCopiesVal) printCopiesVal.textContent = "8 copies";
    if (printSheetCanvas) {
      const pctx = printSheetCanvas.getContext("2d");
      pctx.clearRect(0, 0, printSheetCanvas.width, printSheetCanvas.height);
    }
    memoryCache.printLayout = {
      orientation: "portrait",
      copies: 8,
      borderPx: 2,
      spacingPx: 20,
      marginPx: 30,
      maxFit: 8,
      cols: 2,
      rows: 4
    };

    // Reset enhancement state
    if (toggleEnhancement) toggleEnhancement.checked = false;
    if (enhancementStatusLabel) enhancementStatusLabel.textContent = "Enhancement Disabled";
    if (enhancementBody) enhancementBody.classList.add("disabled-panel");
    if (btnCompareToggle) btnCompareToggle.classList.remove("active");
    if (btnCompareHold) btnCompareHold.classList.remove("active");
    if (enhancementCompareTag) enhancementCompareTag.classList.add("hidden");
    memoryCache.faceEnhancement = {
      enabled: false,
      strength: 50,
      lighting: 10,
      smoothing: 35,
      blemish: 25,
      sharpening: 20,
      compareMode: false,
      splitCompare: false
    };
    applyEnhancementPreset(ENHANCEMENT_PRESETS.reset);

    imgOriginal.src = "";
    faceOverlaysContainer.innerHTML = "";
    cropOverlayWrapper.classList.add("hidden");

    if (passportPreviewCanvas) {
      const ctx = passportPreviewCanvas.getContext("2d");
      ctx.clearRect(0, 0, passportPreviewCanvas.width, passportPreviewCanvas.height);
    }

    emptyState.classList.remove("hidden");
    dualPanelContainer.classList.add("hidden");
    hideError();
  }

  // --- Listeners for Window Resize & Image Load ---
  imgOriginal.addEventListener("load", () => {
    setTimeout(() => {
      updateCropBoxDOM();
      updateFaceOverlays();
      updateLivePassportPreview();
    }, 40);
  });

  window.addEventListener("resize", () => {
    updateCropBoxDOM();
    updateFaceOverlays();
    updateLivePassportPreview();
  });

  smoothnessSlider.addEventListener("input", (e) => {
    smoothnessVal.textContent = parseFloat(e.target.value).toFixed(2);
  });

  // --- Overlay & Toast Helpers ---
  function showOverlay(show) {
    if (show) {
      processingOverlay.classList.remove("hidden");
    } else {
      processingOverlay.classList.add("hidden");
    }
  }

  function setStage(msg, percent) {
    processingStateMsg.textContent = msg;
    progressFill.style.width = `${percent}%`;
  }

  function showError(msg) {
    errorMessage.textContent = msg;
    errorToast.classList.remove("hidden");
  }

  function hideError() {
    errorToast.classList.add("hidden");
  }

  toastClose.addEventListener("click", hideError);

  window.addEventListener("resize", () => {
    if (memoryCache.currentViewMode === "print") {
      updatePrintSheetPreview();
    }
  });
});
