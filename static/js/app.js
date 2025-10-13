/**
 * App.js - PyxelArt Main Application
 * Orchestrates all components and user interactions
 */

class PyxelArtApp {
    constructor() {
        this.currentFiles = [];
        this.currentFileIndex = 0;
        this.batchMode = false;
        this.init();
    }

    /**
     * Initialize application
     */
    async init() {
        // Initialize managers
        presetManager = new PresetManager();
        presetUI = new PresetUI(presetManager);
        effectsManager = new EffectsManager();
        comparisonSlider = new ComparisonSlider();

        // Store in window for global access
        window.presetManager = presetManager;
        window.presetUI = presetUI;
        window.effectsManager = effectsManager;
        window.comparisonSlider = comparisonSlider;

        // Setup UI components
        this.setupDropzone();
        this.setupPreviewControls();
        this.setupExportControls();

        // Check API health
        await this.checkAPIHealth();

        // Load presets from backend
        await this.loadBackendPresets();

        console.log('PyxelArt initialized');
    }

    /**
     * Check API health
     */
    async checkAPIHealth() {
        try {
            const health = await API.checkHealth();
            console.log('API Health:', health);
        } catch (error) {
            console.warn('API health check failed:', error);
        }
    }

    /**
     * Load presets from backend
     */
    async loadBackendPresets() {
        try {
            await presetManager.loadPresetsFromBackend();
            presetUI.renderPresetsList();
        } catch (error) {
            console.warn('Could not load presets from backend:', error);
        }
    }

    /**
     * Setup dropzone for file upload
     */
    setupDropzone() {
        const dropzone = document.getElementById('dropzone');
        const fileInput = document.getElementById('fileInput');
        const selectFileBtn = document.getElementById('selectFileBtn');

        if (!dropzone || !fileInput) return;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        // Highlight drop zone when item is dragged over
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, () => {
                dropzone.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, () => {
                dropzone.classList.remove('dragover');
            });
        });

        // Handle dropped files
        dropzone.addEventListener('drop', (e) => {
            const files = Array.from(e.dataTransfer.files);
            this.handleFiles(files);
        });

        // Handle file input
        if (selectFileBtn) {
            selectFileBtn.addEventListener('click', () => {
                fileInput.click();
            });
        }

        fileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            this.handleFiles(files);
        });
    }

    /**
     * Handle uploaded files
     */
    async handleFiles(files) {
        if (!files || files.length === 0) return;

        // Filter image files
        const imageFiles = files.filter(file => file.type.startsWith('image/'));

        if (imageFiles.length === 0) {
            alert('Por favor selecciona archivos de imagen válidos');
            return;
        }

        this.currentFiles = imageFiles;
        this.currentFileIndex = 0;
        this.batchMode = imageFiles.length > 1;

        // Load first image
        await this.loadImage(this.currentFiles[0]);

        // Show UI sections
        this.showSection('effectsSection');
        this.showSection('pixelartControls');
        this.showSection('exportSection');
        this.showPreviewControls();

        // Update batch info if multiple files
        if (this.batchMode) {
            this.updateBatchInfo();
        }
    }

    /**
     * Load image file
     */
    async loadImage(file) {
        try {
            effectsManager.showLoading(true);

            // Convert to base64
            const base64Data = await ImageUtils.fileToBase64(file);

            // Store in effects manager
            effectsManager.currentImageData = base64Data;
            effectsManager.processedImageData = base64Data;

            // Load and display original image
            const dataURL = ImageUtils.base64ToDataURL(base64Data);
            const img = await ImageUtils.loadImage(dataURL);

            const originalCanvas = document.getElementById('originalCanvas');
            if (originalCanvas) {
                ImageUtils.drawToCanvas(img, originalCanvas);
            }

            await effectsManager.displayPreview(base64Data);

            // Update image info
            this.updateImageInfo(file, img);

            // Generate initial preview with current settings
            effectsManager.schedulePreview();

        } catch (error) {
            console.error('Error loading image:', error);
            alert('Error al cargar imagen: ' + error.message);
        } finally {
            effectsManager.showLoading(false);
        }
    }

    /**
     * Update image info display
     */
    updateImageInfo(file, img) {
        const imageInfo = document.getElementById('imageInfo');
        const fileName = document.getElementById('fileName');
        const imageDimensions = document.getElementById('imageDimensions');
        const fileSize = document.getElementById('fileSize');

        if (imageInfo) imageInfo.style.display = 'block';
        if (fileName) fileName.textContent = file.name;
        if (imageDimensions) imageDimensions.textContent = `${img.width} x ${img.height}`;
        if (fileSize) fileSize.textContent = this.formatFileSize(file.size);
    }

    /**
     * Format file size
     */
    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    /**
     * Update batch processing info
     */
    updateBatchInfo() {
        // Could add a UI element to show "Image 1 of 5" etc.
        console.log(`Batch mode: ${this.currentFileIndex + 1} of ${this.currentFiles.length}`);
    }

    /**
     * Setup preview controls
     */
    setupPreviewControls() {
        const toggleComparisonBtn = document.getElementById('toggleComparison');
        const resetEffectsBtn = document.getElementById('resetEffects');
        const applyFullResBtn = document.getElementById('applyFullRes');

        if (toggleComparisonBtn) {
            toggleComparisonBtn.addEventListener('click', () => {
                this.toggleComparison();
            });
        }

        if (resetEffectsBtn) {
            resetEffectsBtn.addEventListener('click', () => {
                effectsManager.resetEffects();
            });
        }

        if (applyFullResBtn) {
            applyFullResBtn.addEventListener('click', () => {
                effectsManager.applyFullResolution();
            });
        }
    }

    /**
     * Setup export controls
     */
    setupExportControls() {
        const exportBtn = document.getElementById('exportImage');

        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                effectsManager.exportImage();
            });
        }
    }

    /**
     * Toggle comparison view
     */
    toggleComparison() {
        if (!effectsManager.currentImageData || !effectsManager.processedImageData) {
            return;
        }

        if (comparisonSlider.isActive) {
            comparisonSlider.hide();
            // Show preview canvas
            const previewCanvas = document.getElementById('previewCanvas');
            if (previewCanvas) previewCanvas.style.display = 'block';
        } else {
            // Hide preview canvas
            const previewCanvas = document.getElementById('previewCanvas');
            if (previewCanvas) previewCanvas.style.display = 'none';

            comparisonSlider.show(
                effectsManager.currentImageData,
                effectsManager.processedImageData
            );
        }
    }

    /**
     * Show section
     */
    showSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            section.style.display = 'block';
        }
    }

    /**
     * Show preview controls
     */
    showPreviewControls() {
        const previewControls = document.getElementById('previewControls');
        if (previewControls) {
            previewControls.style.display = 'flex';
        }
    }

    /**
     * Process batch of images
     */
    async processBatch() {
        if (!this.batchMode || this.currentFiles.length === 0) {
            alert('Carga múltiples imágenes para usar modo batch');
            return;
        }

        const settings = effectsManager.getCurrentSettings();

        if (settings.effects.length === 0) {
            alert('Selecciona al menos un efecto');
            return;
        }

        effectsManager.showLoading(true);

        try {
            // Convert all files to base64
            const imagesData = await Promise.all(
                this.currentFiles.map(file => ImageUtils.fileToBase64(file))
            );

            // Process batch
            const results = await API.batchProcess(imagesData, settings);

            // Download all results
            if (results.results && Array.isArray(results.results)) {
                results.results.forEach((resultData, index) => {
                    const format = document.getElementById('exportFormat')?.value || 'webp';
                    const quality = parseInt(document.getElementById('exportQuality')?.value || 90);

                    // Create blob and download
                    const blob = this.base64ToBlob(resultData, `image/${format}`);
                    const filename = `pyxelart_${index + 1}.${format}`;
                    ImageUtils.downloadBlob(blob, filename);
                });

                alert(`${results.results.length} imágenes procesadas correctamente`);
            }
        } catch (error) {
            console.error('Batch processing failed:', error);
            alert('Error en procesamiento batch: ' + error.message);
        } finally {
            effectsManager.showLoading(false);
        }
    }

    /**
     * Convert base64 to blob
     */
    base64ToBlob(base64, mimeType) {
        const byteCharacters = atob(base64);
        const byteArrays = [];

        for (let offset = 0; offset < byteCharacters.length; offset += 512) {
            const slice = byteCharacters.slice(offset, offset + 512);
            const byteNumbers = new Array(slice.length);

            for (let i = 0; i < slice.length; i++) {
                byteNumbers[i] = slice.charCodeAt(i);
            }

            const byteArray = new Uint8Array(byteNumbers);
            byteArrays.push(byteArray);
        }

        return new Blob(byteArrays, { type: mimeType });
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new PyxelArtApp();
});
