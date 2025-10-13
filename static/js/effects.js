/**
 * Effects.js - PyxelArt Effects Management and Processing
 */

class EffectsManager {
    constructor() {
        this.currentImage = null;
        this.currentImageData = null;
        this.processedImageData = null;
        this.previewThrottleTimeout = null;
        this.previewDelay = 500; // ms
        this.isProcessing = false;
        this.stats = {
            activeEffects: 0,
            processTime: 0,
            previewSize: '-'
        };
        this.init();
    }

    init() {
        this.setupEffectControls();
        this.updateStats();
    }

    /**
     * Setup effect control listeners
     */
    setupEffectControls() {
        // Effect checkboxes
        document.querySelectorAll('.effect-checkbox input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.toggleEffectControls(checkbox.value, checkbox.checked);
                this.schedulePreview();
            });
        });

        // Pixel Art controls
        this.setupRangeControl('colors', 'colorsValue');
        this.setupRangeControl('pixelSize', 'pixelSizeValue');
        this.setupRangeControl('noiseIntensity', 'noiseIntensityValue');
        document.getElementById('addNoise')?.addEventListener('change', () => this.schedulePreview());

        // Chromatic Aberration controls
        this.setupRangeControl('aberrationIntensity', 'aberrationIntensityValue', (val) => parseFloat(val).toFixed(1));
        document.getElementById('lensEffect')?.addEventListener('change', () => this.schedulePreview());

        // Dialog controls
        document.getElementById('dialogText')?.addEventListener('input', () => this.schedulePreview());

        // Glitch controls
        this.setupRangeControl('glitchIntensity', 'glitchIntensityValue');
        this.setupRangeControl('scanlineIntensity', 'scanlineIntensityValue', (val) => parseFloat(val).toFixed(2));

        // Export controls
        document.getElementById('exportFormat')?.addEventListener('change', (e) => {
            this.toggleQualityControl(e.target.value);
        });
        this.setupRangeControl('exportQuality', 'exportQualityValue');
    }

    /**
     * Setup range control with live value display
     */
    setupRangeControl(inputId, valueId, formatter = null) {
        const input = document.getElementById(inputId);
        const valueDisplay = document.getElementById(valueId);

        if (input && valueDisplay) {
            input.addEventListener('input', (e) => {
                const value = formatter ? formatter(e.target.value) : e.target.value;
                valueDisplay.textContent = value;
                this.schedulePreview();
            });
        }
    }

    /**
     * Toggle effect-specific controls
     */
    toggleEffectControls(effectType, enabled) {
        const controlsMap = {
            'pixelart': 'pixelartControls',
            'chromatic': 'chromaticControls',
            'dialog': 'dialogControls',
            'glitch_scanlines': 'glitchControls',
            'glitch_blocks': 'glitchControls'
        };

        const controlsId = controlsMap[effectType];
        if (controlsId) {
            const controlsElement = document.getElementById(controlsId);
            if (controlsElement) {
                controlsElement.style.display = enabled ? 'block' : 'none';
            }
        }

        this.updateActiveEffectsCount();
    }

    /**
     * Toggle quality control visibility based on format
     */
    toggleQualityControl(format) {
        const qualityGroup = document.getElementById('qualityGroup');
        if (qualityGroup) {
            // Hide quality for PNG (lossless)
            qualityGroup.style.display = (format === 'png') ? 'none' : 'block';
        }
    }

    /**
     * Get current settings from UI
     */
    getCurrentSettings() {
        const settings = {
            effects: [],
            // Pixel Art
            colors: parseInt(document.getElementById('colors')?.value || 16),
            pixel_size: parseInt(document.getElementById('pixelSize')?.value || 4),
            add_noise: document.getElementById('addNoise')?.checked || false,
            noise_intensity: parseInt(document.getElementById('noiseIntensity')?.value || 15),
            // Chromatic Aberration
            aberration_intensity: parseFloat(document.getElementById('aberrationIntensity')?.value || 1.0),
            lens_effect: document.getElementById('lensEffect')?.checked || false,
            // Dialog
            dialog_text: document.getElementById('dialogText')?.value || 'GAME OVER',
            // Glitch
            glitch_intensity: parseInt(document.getElementById('glitchIntensity')?.value || 10),
            scanline_intensity: parseFloat(document.getElementById('scanlineIntensity')?.value || 0.1)
        };

        // Get active effects
        document.querySelectorAll('.effect-checkbox input[type="checkbox"]:checked').forEach(checkbox => {
            settings.effects.push(checkbox.value);
        });

        return settings;
    }

    /**
     * Apply preset settings to UI
     */
    applyPresetSettings(preset) {
        // Clear all effect checkboxes
        document.querySelectorAll('.effect-checkbox input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = false;
        });

        // Hide all effect controls
        ['pixelartControls', 'chromaticControls', 'dialogControls', 'glitchControls'].forEach(id => {
            const element = document.getElementById(id);
            if (element) element.style.display = 'none';
        });

        // Apply effects
        if (preset.effects) {
            preset.effects.forEach(effect => {
                const checkbox = document.querySelector(`.effect-checkbox input[value="${effect}"]`);
                if (checkbox) {
                    checkbox.checked = true;
                    this.toggleEffectControls(effect, true);
                }
            });
        }

        // Apply parameters
        const params = preset.params || {};

        // Pixel Art
        if (params.colors !== undefined) {
            this.setRangeValue('colors', params.colors, 'colorsValue');
        }
        if (params.pixel_size !== undefined) {
            this.setRangeValue('pixelSize', params.pixel_size, 'pixelSizeValue');
        }
        if (params.add_noise !== undefined) {
            const checkbox = document.getElementById('addNoise');
            if (checkbox) checkbox.checked = params.add_noise;
        }
        if (params.noise_intensity !== undefined) {
            this.setRangeValue('noiseIntensity', params.noise_intensity, 'noiseIntensityValue');
        }

        // Chromatic Aberration
        if (params.aberration_intensity !== undefined) {
            this.setRangeValue('aberrationIntensity', params.aberration_intensity, 'aberrationIntensityValue',
                (val) => parseFloat(val).toFixed(1));
        }
        if (params.lens_effect !== undefined) {
            const checkbox = document.getElementById('lensEffect');
            if (checkbox) checkbox.checked = params.lens_effect;
        }

        // Dialog
        if (params.dialog_text !== undefined) {
            const input = document.getElementById('dialogText');
            if (input) input.value = params.dialog_text;
        }

        // Glitch
        if (params.glitch_intensity !== undefined) {
            this.setRangeValue('glitchIntensity', params.glitch_intensity, 'glitchIntensityValue');
        }
        if (params.scanline_intensity !== undefined) {
            this.setRangeValue('scanlineIntensity', params.scanline_intensity, 'scanlineIntensityValue',
                (val) => parseFloat(val).toFixed(2));
        }

        // Update UI and generate preview
        this.updateActiveEffectsCount();
        this.schedulePreview();
    }

    /**
     * Set range input value and update display
     */
    setRangeValue(inputId, value, valueId, formatter = null) {
        const input = document.getElementById(inputId);
        const valueDisplay = document.getElementById(valueId);

        if (input) {
            input.value = value;
            if (valueDisplay) {
                const displayValue = formatter ? formatter(value) : value;
                valueDisplay.textContent = displayValue;
            }
        }
    }

    /**
     * Schedule preview generation (throttled)
     */
    schedulePreview() {
        if (!this.currentImageData) return;

        // Clear existing timeout
        if (this.previewThrottleTimeout) {
            clearTimeout(this.previewThrottleTimeout);
        }

        // Schedule new preview
        this.previewThrottleTimeout = setTimeout(() => {
            this.generatePreview();
        }, this.previewDelay);
    }

    /**
     * Generate preview
     */
    async generatePreview() {
        if (!this.currentImageData || this.isProcessing) return;

        const settings = this.getCurrentSettings();

        // If no effects selected, show original
        if (settings.effects.length === 0) {
            this.displayPreview(this.currentImageData);
            this.processedImageData = this.currentImageData;
            return;
        }

        this.isProcessing = true;
        this.showLoading(true);

        const startTime = performance.now();

        try {
            const previewData = await API.generatePreview(this.currentImageData, settings);
            this.processedImageData = previewData;
            this.displayPreview(previewData);

            const endTime = performance.now();
            this.stats.processTime = ((endTime - startTime) / 1000).toFixed(2) + 's';
            this.updateStats();
        } catch (error) {
            console.error('Preview generation failed:', error);
            alert('Error al generar preview: ' + error.message);
        } finally {
            this.isProcessing = false;
            this.showLoading(false);
        }
    }

    /**
     * Apply effects at full resolution
     */
    async applyFullResolution() {
        if (!this.currentImageData || this.isProcessing) return;

        const settings = this.getCurrentSettings();

        if (settings.effects.length === 0) {
            alert('Selecciona al menos un efecto');
            return;
        }

        this.isProcessing = true;
        this.showLoading(true);

        try {
            const resultData = await API.applyEffects(this.currentImageData, settings);
            this.processedImageData = resultData;
            this.displayPreview(resultData);
            alert('Efectos aplicados en alta resolución');
        } catch (error) {
            console.error('Full resolution processing failed:', error);
            alert('Error al aplicar efectos: ' + error.message);
        } finally {
            this.isProcessing = false;
            this.showLoading(false);
        }
    }

    /**
     * Display preview on canvas
     */
    async displayPreview(base64Data) {
        const canvas = document.getElementById('previewCanvas');
        const placeholder = document.getElementById('previewPlaceholder');

        if (!canvas) return;

        try {
            const dataURL = ImageUtils.base64ToDataURL(base64Data);
            const img = await ImageUtils.loadImage(dataURL);

            ImageUtils.drawToCanvas(img, canvas);

            if (placeholder) {
                placeholder.style.display = 'none';
            }

            // Update preview size stat
            this.stats.previewSize = `${img.width}x${img.height}`;
            this.updateStats();
        } catch (error) {
            console.error('Error displaying preview:', error);
        }
    }

    /**
     * Update active effects count
     */
    updateActiveEffectsCount() {
        const count = document.querySelectorAll('.effect-checkbox input[type="checkbox"]:checked').length;
        this.stats.activeEffects = count;
        this.updateStats();
    }

    /**
     * Update statistics display
     */
    updateStats() {
        const activeEffectsEl = document.getElementById('activeEffects');
        const processTimeEl = document.getElementById('processTime');
        const previewSizeEl = document.getElementById('previewSize');

        if (activeEffectsEl) activeEffectsEl.textContent = this.stats.activeEffects;
        if (processTimeEl) processTimeEl.textContent = this.stats.processTime || '-';
        if (previewSizeEl) previewSizeEl.textContent = this.stats.previewSize || '-';
    }

    /**
     * Show/hide loading indicator
     */
    showLoading(show) {
        const loadingIndicator = document.getElementById('loadingIndicator');
        if (loadingIndicator) {
            loadingIndicator.style.display = show ? 'block' : 'none';
        }
    }

    /**
     * Reset all effects to default
     */
    resetEffects() {
        // Uncheck all effects
        document.querySelectorAll('.effect-checkbox input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = false;
        });

        // Check pixel art by default
        const pixelartCheckbox = document.getElementById('effect-pixelart');
        if (pixelartCheckbox) {
            pixelartCheckbox.checked = true;
        }

        // Reset to default values
        this.setRangeValue('colors', 16, 'colorsValue');
        this.setRangeValue('pixelSize', 4, 'pixelSizeValue');
        this.setRangeValue('noiseIntensity', 15, 'noiseIntensityValue');
        this.setRangeValue('aberrationIntensity', 1.0, 'aberrationIntensityValue', (val) => parseFloat(val).toFixed(1));
        this.setRangeValue('glitchIntensity', 10, 'glitchIntensityValue');
        this.setRangeValue('scanlineIntensity', 0.1, 'scanlineIntensityValue', (val) => parseFloat(val).toFixed(2));

        const addNoiseCheckbox = document.getElementById('addNoise');
        if (addNoiseCheckbox) addNoiseCheckbox.checked = true;

        const lensEffectCheckbox = document.getElementById('lensEffect');
        if (lensEffectCheckbox) lensEffectCheckbox.checked = false;

        const dialogText = document.getElementById('dialogText');
        if (dialogText) dialogText.value = 'GAME OVER';

        // Update UI
        this.toggleEffectControls('pixelart', true);
        ['chromatic', 'dialog', 'glitch_scanlines', 'glitch_blocks'].forEach(effect => {
            this.toggleEffectControls(effect, false);
        });

        this.updateActiveEffectsCount();

        // Show original image
        if (this.currentImageData) {
            this.displayPreview(this.currentImageData);
            this.processedImageData = this.currentImageData;
        }
    }

    /**
     * Export processed image
     */
    async exportImage() {
        if (!this.processedImageData) {
            alert('No hay imagen procesada para exportar');
            return;
        }

        const format = document.getElementById('exportFormat')?.value || 'webp';
        const quality = parseInt(document.getElementById('exportQuality')?.value || 90);

        this.showLoading(true);

        try {
            const blob = await API.exportImage(this.processedImageData, format, {
                quality: quality,
                dpi: 300 // For TIFF
            });

            const filename = `pyxelart_${Date.now()}.${format}`;
            ImageUtils.downloadBlob(blob, filename);
        } catch (error) {
            console.error('Export failed:', error);
            alert('Error al exportar imagen: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }
}

/**
 * Comparison Slider Manager
 */
class ComparisonSlider {
    constructor() {
        this.container = document.getElementById('comparisonContainer');
        this.beforeCanvas = document.getElementById('beforeCanvas');
        this.afterCanvas = document.getElementById('afterCanvas');
        this.handle = document.getElementById('sliderHandle');
        this.isActive = false;
        this.isDragging = false;
        this.sliderPosition = 50; // percentage
        this.init();
    }

    init() {
        if (!this.handle || !this.container) return;

        this.handle.addEventListener('mousedown', (e) => this.startDrag(e));
        document.addEventListener('mousemove', (e) => this.drag(e));
        document.addEventListener('mouseup', () => this.stopDrag());
    }

    /**
     * Show comparison slider
     */
    async show(beforeData, afterData) {
        if (!this.container || !this.beforeCanvas || !this.afterCanvas) return;

        try {
            // Load images
            const beforeImg = await ImageUtils.loadImage(ImageUtils.base64ToDataURL(beforeData));
            const afterImg = await ImageUtils.loadImage(ImageUtils.base64ToDataURL(afterData));

            // Draw to canvases
            ImageUtils.drawToCanvas(beforeImg, this.beforeCanvas);
            ImageUtils.drawToCanvas(afterImg, this.afterCanvas);

            // Show container
            this.container.style.display = 'block';
            this.isActive = true;

            // Set initial clip
            this.updateClip();
        } catch (error) {
            console.error('Error showing comparison:', error);
        }
    }

    /**
     * Hide comparison slider
     */
    hide() {
        if (this.container) {
            this.container.style.display = 'none';
            this.isActive = false;
        }
    }

    /**
     * Start dragging
     */
    startDrag(e) {
        this.isDragging = true;
        e.preventDefault();
    }

    /**
     * Drag handler
     */
    drag(e) {
        if (!this.isDragging || !this.container) return;

        const rect = this.container.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const percentage = (x / rect.width) * 100;

        this.sliderPosition = Math.max(0, Math.min(100, percentage));
        this.updateClip();
    }

    /**
     * Stop dragging
     */
    stopDrag() {
        this.isDragging = false;
    }

    /**
     * Update clip path
     */
    updateClip() {
        if (!this.handle || !this.afterCanvas) return;

        this.handle.style.left = `${this.sliderPosition}%`;
        this.afterCanvas.style.clipPath = `inset(0 ${100 - this.sliderPosition}% 0 0)`;
    }
}

// Global instances (will be initialized in app.js)
let effectsManager;
let comparisonSlider;
