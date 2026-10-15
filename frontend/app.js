// Snap2Print Instant Pro Frontend Logic (Decoupled Stage A AI + Zero-Latency Stage B Compositing)

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const browseBtn = document.getElementById("browseBtn");
  const dropzoneContent = document.getElementById("dropzoneContent");
  const fileInfoBar = document.getElementById("fileInfoBar");
  const fileName = document.getElementById("fileName");
  const fileSize = document.getElementById("fileSize");
  const clearFileBtn = document.getElementById("clearFileBtn");

  const methodBanner = document.getElementById("methodBanner");
  const methodLabel = document.getElementById("methodLabel");
  const methodSub = document.getElementById("methodSub");
  const methodModeSelect = document.getElementById("methodModeSelect");
  const smoothnessSlider = document.getElementById("smoothnessSlider");
  const smoothnessVal = document.getElementById("smoothnessVal");
  const compareModelsBtn = document.getElementById("compareModelsBtn");

  const processBtn = document.getElementById("processBtn");
  const btnSpinner = document.getElementById("btnSpinner");
  const btnText = document.getElementById("btnText");

  const bgOptions = document.querySelectorAll(".bg-option-item");
  const customColorContainer = document.getElementById("customColorContainer");
  const colorPickerInput = document.getElementById("colorPickerInput");
  const colorHexInput = document.getElementById("colorHexInput");
  const customColorSwatch = document.getElementById("customColorSwatch");

  const debugCard = document.getElementById("debugCard");
  const dbgSeg = document.getElementById("dbgSeg");
  const dbgRefine = document.getElementById("dbgRefine");
  const dbgColorLatency = document.getElementById("dbgColorLatency");
  const dbgExport = document.getElementById("dbgExport");
  const dbgPreviewRes = document.getElementById("dbgPreviewRes");
  const dbgExportRes = document.getElementById("dbgExportRes");

  const emptyState = document.getElementById("emptyState");
  const dualPanelContainer = document.getElementById("dualPanelContainer");
  const imgOriginal = document.getElementById("imgOriginal");
  const imgProcessed = document.getElementById("imgProcessed");
  const studioBgLayer = document.getElementById("studioBgLayer");

  const comparisonGridContainer = document.getElementById("comparisonGridContainer");
  const imgCmpB = document.getElementById("imgCmpB");
  const imgCmpU = document.getElementById("imgCmpU");
  const imgCmpC = document.getElementById("imgCmpC");
  const cmpTimeB = document.getElementById("cmpTimeB");
  const cmpTimeU = document.getElementById("cmpTimeU");
  const cmpTimeC = document.getElementById("cmpTimeC");
  const cmpMetaB = document.getElementById("cmpMetaB");
  const cmpMetaU = document.getElementById("cmpMetaU");
  const cmpMetaC = document.getElementById("cmpMetaC");

  const tabOriginal = document.getElementById("tabOriginal");
  const tabProcessed = document.getElementById("tabProcessed");
  const tabSplit = document.getElementById("tabSplit");
  const tabCompare = document.getElementById("tabCompare");
  const downloadBtn = document.getElementById("downloadBtn");
  const downloadBtnText = document.getElementById("downloadBtnText");
  const downloadSpinner = document.getElementById("downloadSpinner");
  const downloadIcon = document.getElementById("downloadIcon");

  const processingOverlay = document.getElementById("processingOverlay");
  const processingStateMsg = document.getElementById("processingStateMsg");
  const progressFill = document.getElementById("progressFill");

  const errorToast = document.getElementById("errorToast");
  const errorMessage = document.getElementById("errorMessage");
  const toastClose = document.getElementById("toastClose");

  // In-Memory Client Cache
  const memoryCache = {
    currentFile: null,
    sessionId: null,
    activeBgChoice: "transparent",
    activeCustomColor: "#1877f2",
    originalPreviewUrl: null,
    transparentPreviewUrl: null,
    maskPreviewUrl: null,
    originalDimensions: null,
    previewDimensions: null,
    currentViewMode: "split"
  };

  // 1. File Upload & Drag-and-Drop
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
      showError(`Unsupported file format '${ext}'. Please choose a JPG, PNG, WEBP, or BMP.`);
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
    processBtn.disabled = false;
    compareModelsBtn.disabled = false;
    hideError();

    // Instant local preview in Original panel
    const reader = new FileReader();
    reader.onload = (e) => {
      memoryCache.originalPreviewUrl = e.target.result;
      imgOriginal.src = memoryCache.originalPreviewUrl;
      emptyState.classList.add("hidden");
      dualPanelContainer.classList.remove("hidden");
      comparisonGridContainer.classList.add("hidden");
      setViewMode(memoryCache.currentViewMode === "compare" ? "split" : memoryCache.currentViewMode);
    };
    reader.readAsDataURL(file);
  }

  function resetState() {
    memoryCache.currentFile = null;
    memoryCache.sessionId = null;
    memoryCache.originalPreviewUrl = null;
    memoryCache.transparentPreviewUrl = null;
    memoryCache.maskPreviewUrl = null;
    fileInput.value = "";
    fileInfoBar.classList.add("hidden");
    dropzoneContent.classList.remove("hidden");
    processBtn.disabled = true;
    compareModelsBtn.disabled = true;
    methodBanner.classList.add("hidden");
    debugCard.classList.add("hidden");
    tabCompare.classList.add("hidden");
    downloadBtn.classList.add("disabled");
    imgOriginal.src = "";
    imgProcessed.src = "";
    emptyState.classList.remove("hidden");
    dualPanelContainer.classList.add("hidden");
    comparisonGridContainer.classList.add("hidden");
    hideError();
  }

  smoothnessSlider.addEventListener("input", (e) => {
    smoothnessVal.textContent = parseFloat(e.target.value).toFixed(2);
  });

  // 2. STAGE B: Instant Zero-Lag Browser Background Compositing (<1 ms)
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

      // Instant local background swap (0 API requests!)
      applyInstantBackground();
    });
  });

  colorPickerInput.addEventListener("input", (e) => {
    memoryCache.activeCustomColor = e.target.value;
    colorHexInput.value = memoryCache.activeCustomColor;
    customColorSwatch.style.backgroundColor = memoryCache.activeCustomColor;
    if (memoryCache.activeBgChoice === "custom") applyInstantBackground();
  });

  colorHexInput.addEventListener("change", (e) => {
    let val = e.target.value.trim();
    if (!val.startsWith("#")) val = "#" + val;
    if (/^#[0-9A-Fa-f]{6}$/.test(val)) {
      memoryCache.activeCustomColor = val;
      colorPickerInput.value = val;
      customColorSwatch.style.backgroundColor = val;
      if (memoryCache.activeBgChoice === "custom") applyInstantBackground();
    }
  });

  function applyInstantBackground() {
    const t0 = performance.now();
    const choice = memoryCache.activeBgChoice;
    let targetColor = "transparent";

    if (choice === "transparent") {
      targetColor = "transparent";
    } else if (choice === "white") {
      targetColor = "#ffffff";
    } else if (choice === "blue") {
      targetColor = "#1877f2";
    } else if (choice === "custom") {
      targetColor = memoryCache.activeCustomColor;
    }

    if (imgProcessed) {
      imgProcessed.style.backgroundColor = targetColor;
    }
    if (studioBgLayer) {
      studioBgLayer.style.backgroundColor = targetColor;
    }

    const latency = Math.max(1, Math.round(performance.now() - t0));
    dbgColorLatency.textContent = `${latency} ms (Instant Browser)`;
  }

  // 3. STAGE A: Expensive AI Processing (Upload once, run once)
  processBtn.addEventListener("click", async () => {
    if (!memoryCache.currentFile) return;

    showOverlay(true);
    hideError();

    const isStudio = methodModeSelect.value === "birefnet";
    setStage(isStudio ? "Analyzing photo for Studio Quality..." : "Analyzing photo...", 20);
    const t1 = setTimeout(() => {
      setStage(isStudio ? "Running BiRefNet-Portrait (Studio Quality)..." : "Running Fast AI Segmentation...", 50);
    }, 300);
    const t2 = setTimeout(() => setStage("Refining edges...", 80), isStudio ? 3000 : 700);
    const t3 = setTimeout(() => setStage("Preparing studio preview...", 95), isStudio ? 6000 : 1000);

    const formData = new FormData();
    formData.append("file", memoryCache.currentFile);
    formData.append("method_mode", methodModeSelect.value);
    formData.append("smoothness", smoothnessSlider.value);

    try {
      const response = await fetch("/api/photo/process-background", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Processing failed.");

      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);

      memoryCache.sessionId = data.session_id;
      memoryCache.transparentPreviewUrl = data.previews.transparent_preview;
      memoryCache.maskPreviewUrl = data.previews.mask_preview;
      memoryCache.originalDimensions = data.original_dimensions;
      memoryCache.previewDimensions = data.preview_dimensions;

      // Update Processed Image preview with Transparent Subject
      imgProcessed.src = memoryCache.transparentPreviewUrl;
      imgOriginal.src = data.previews.original;

      // Apply initial background color locally
      applyInstantBackground();

      // Update Method Banner
      methodLabel.textContent = `Engine: ${data.method_info.selected_method}`;
      methodSub.textContent = data.method_info.reason;
      methodBanner.classList.remove("hidden");

      // Update Telemetry
      dbgSeg.textContent = `${data.timings.segmentation_ms} ms`;
      dbgRefine.textContent = `${data.timings.mask_refinement_ms} ms`;
      dbgPreviewRes.textContent = `${data.preview_dimensions.width} × ${data.preview_dimensions.height}`;
      dbgExportRes.textContent = `${data.original_dimensions.width} × ${data.original_dimensions.height}`;
      debugCard.classList.remove("hidden");

      // Enable Download
      downloadBtn.classList.remove("disabled");

      setViewMode("split");
    } catch (err) {
      showError(err.message || "Failed to process photo.");
    } finally {
      showOverlay(false);
    }
  });

  // 4. ON-DEMAND FULL-RESOLUTION EXPORT (Triggered ONLY on Download Click)
  downloadBtn.addEventListener("click", async () => {
    if (!memoryCache.sessionId) return;

    downloadBtn.classList.add("disabled");
    downloadSpinner.classList.remove("hidden");
    downloadIcon.classList.add("hidden");
    downloadBtnText.textContent = "Exporting Full Res...";

    const t0 = performance.now();
    const formData = new FormData();
    formData.append("session_id", memoryCache.sessionId);
    formData.append("bg_type", memoryCache.activeBgChoice);
    if (memoryCache.activeBgChoice === "custom") {
      formData.append("custom_color", memoryCache.activeCustomColor);
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
      tempLink.setAttribute("download", `snap2print_${memoryCache.sessionId}_${memoryCache.activeBgChoice}.png`);
      document.body.appendChild(tempLink);
      tempLink.click();
      document.body.removeChild(tempLink);
    } catch (err) {
      showError(err.message || "Failed to export full resolution image.");
    } finally {
      downloadBtn.classList.remove("disabled");
      downloadSpinner.classList.add("hidden");
      downloadIcon.classList.remove("hidden");
      downloadBtnText.textContent = "Download Full Res";
    }
  });

  // 5. Compare Models Action (Advanced Debug Mode)
  compareModelsBtn.addEventListener("click", async () => {
    if (!memoryCache.currentFile) return;

    showOverlay(true);
    setStage("Executing 3-way Model Comparison (BiRefNet vs U2NetP vs Chroma)...", 40);

    const formData = new FormData();
    formData.append("file", memoryCache.currentFile);
    formData.append("bg_type", memoryCache.activeBgChoice === "transparent" ? "white" : memoryCache.activeBgChoice);

    try {
      const resp = await fetch("/api/photo/compare-models", {
        method: "POST",
        body: formData
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.detail || "Comparison failed.");

      const res = data.results;

      // BiRefNet
      if (res.birefnet && res.birefnet.status === "Success") {
        imgCmpB.src = res.birefnet.preview;
        cmpTimeB.textContent = `${res.birefnet.time_ms} ms`;
        cmpMetaB.textContent = `Inference: ${res.birefnet.inference_res} • Studio Pro`;
      }

      // U2NetP
      if (res.u2netp && res.u2netp.status === "Success") {
        imgCmpU.src = res.u2netp.preview;
        cmpTimeU.textContent = `${res.u2netp.time_ms} ms`;
        cmpMetaU.textContent = `Inference: ${res.u2netp.inference_res} • Lightweight`;
      }

      // Chroma
      if (res.chroma_key && res.chroma_key.status === "Success") {
        imgCmpC.src = res.chroma_key.preview;
        cmpTimeC.textContent = `${res.chroma_key.time_ms} ms`;
        cmpMetaC.textContent = `Uniformity: ${res.chroma_key.uniformity_score} • Fast`;
      }

      tabCompare.classList.remove("hidden");
      setViewMode("compare");
    } catch (err) {
      showError(err.message || "Model comparison failed.");
    } finally {
      showOverlay(false);
    }
  });

  // 6. View Tabs: [ Original ] [ Processed ] [ Split View ] [ Compare View ]
  tabOriginal.addEventListener("click", () => setViewMode("original"));
  tabProcessed.addEventListener("click", () => setViewMode("processed"));
  tabSplit.addEventListener("click", () => setViewMode("split"));
  tabCompare.addEventListener("click", () => setViewMode("compare"));

  function setViewMode(mode) {
    memoryCache.currentViewMode = mode;
    [tabOriginal, tabProcessed, tabSplit, tabCompare].forEach((b) => b.classList.remove("active"));
    dualPanelContainer.classList.remove("single-mode-original", "single-mode-processed", "hidden");
    comparisonGridContainer.classList.add("hidden");

    if (mode === "original") {
      tabOriginal.classList.add("active");
      dualPanelContainer.classList.add("single-mode-original");
    } else if (mode === "processed") {
      tabProcessed.classList.add("active");
      dualPanelContainer.classList.add("single-mode-processed");
    } else if (mode === "compare") {
      tabCompare.classList.add("active");
      dualPanelContainer.classList.add("hidden");
      comparisonGridContainer.classList.remove("hidden");
    } else {
      tabSplit.classList.add("active");
    }
  }

  // Overlay Helpers
  function showOverlay(show) {
    if (show) {
      processingOverlay.classList.remove("hidden");
      processBtn.disabled = true;
      compareModelsBtn.disabled = true;
    } else {
      processingOverlay.classList.add("hidden");
      processBtn.disabled = !memoryCache.currentFile;
      compareModelsBtn.disabled = !memoryCache.currentFile;
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
});
