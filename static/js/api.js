/**
 * API.js - PyxelArt REST API Communication Layer
 * Handles all communication with the Flask backend
 */

const API = {
    baseURL: window.location.origin,

    /**
     * Check API health
     */
    async checkHealth() {
        try {
            const response = await fetch(`${this.baseURL}/health`);
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            return { status: 'error', error: error.message };
        }
    },

    /**
     * Get available effects
     */
    async getEffects() {
        try {
            const response = await fetch(`${this.baseURL}/api/effects`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Get effects failed:', error);
            throw error;
        }
    },

    /**
     * Generate preview (low resolution for speed)
     * @param {string} imageData - Base64 encoded image
     * @param {object} params - Effect parameters
     */
    async generatePreview(imageData, params) {
        try {
            const response = await fetch(`${this.baseURL}/api/preview`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    imageData: imageData,
                    ...params
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }

            const data = await response.json();
            return data.preview;
        } catch (error) {
            console.error('Preview generation failed:', error);
            throw error;
        }
    },

    /**
     * Apply effects to full resolution image
     * @param {string} imageData - Base64 encoded image
     * @param {object} params - Effect parameters
     */
    async applyEffects(imageData, params) {
        try {
            const response = await fetch(`${this.baseURL}/api/apply-effects`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    imageData: imageData,
                    ...params
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }

            const data = await response.json();
            return data.result;
        } catch (error) {
            console.error('Apply effects failed:', error);
            throw error;
        }
    },

    /**
     * Export image in specific format
     * @param {string} imageData - Base64 encoded image
     * @param {string} format - Output format (png, jpg, webp, tiff)
     * @param {object} options - Export options (quality, dpi)
     */
    async exportImage(imageData, format, options = {}) {
        try {
            const response = await fetch(`${this.baseURL}/api/export`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    imageData: imageData,
                    format: format,
                    ...options
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }

            // Return blob for download
            return await response.blob();
        } catch (error) {
            console.error('Export failed:', error);
            throw error;
        }
    },

    /**
     * Get all presets
     */
    async getPresets() {
        try {
            const response = await fetch(`${this.baseURL}/api/presets`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Get presets failed:', error);
            throw error;
        }
    },

    /**
     * Get specific preset by ID
     * @param {string} presetId - Preset ID
     */
    async getPreset(presetId) {
        try {
            const response = await fetch(`${this.baseURL}/api/presets/${presetId}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Get preset failed:', error);
            throw error;
        }
    },

    /**
     * Save new preset
     * @param {object} preset - Preset data
     */
    async savePreset(preset) {
        try {
            const response = await fetch(`${this.baseURL}/api/presets`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(preset)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Save preset failed:', error);
            throw error;
        }
    },

    /**
     * Delete preset
     * @param {string} presetId - Preset ID to delete
     */
    async deletePreset(presetId) {
        try {
            const response = await fetch(`${this.baseURL}/api/presets/${presetId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Delete preset failed:', error);
            throw error;
        }
    },

    /**
     * Process batch of images
     * @param {Array<string>} images - Array of base64 encoded images
     * @param {object} params - Effect parameters or preset
     */
    async batchProcess(images, params) {
        try {
            const response = await fetch(`${this.baseURL}/api/batch-process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    images: images,
                    ...params
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Batch process failed:', error);
            throw error;
        }
    }
};

/**
 * Utility functions for image encoding/decoding
 */
const ImageUtils = {
    /**
     * Convert File to base64 string
     * @param {File} file - Image file
     * @returns {Promise<string>} Base64 string
     */
    fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                // Extract base64 data (remove data:image/...;base64, prefix)
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    },

    /**
     * Convert base64 string to data URL
     * @param {string} base64 - Base64 encoded image
     * @param {string} mimeType - MIME type (default: image/png)
     * @returns {string} Data URL
     */
    base64ToDataURL(base64, mimeType = 'image/png') {
        return `data:${mimeType};base64,${base64}`;
    },

    /**
     * Load image from data URL
     * @param {string} dataURL - Data URL
     * @returns {Promise<HTMLImageElement>}
     */
    loadImage(dataURL) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = reject;
            img.src = dataURL;
        });
    },

    /**
     * Draw image to canvas
     * @param {HTMLImageElement} img - Image element
     * @param {HTMLCanvasElement} canvas - Canvas element
     */
    drawToCanvas(img, canvas) {
        const ctx = canvas.getContext('2d');
        canvas.width = img.naturalWidth || img.width;
        canvas.height = img.naturalHeight || img.height;
        ctx.drawImage(img, 0, 0);
    },

    /**
     * Get canvas as base64
     * @param {HTMLCanvasElement} canvas - Canvas element
     * @param {string} format - Output format (default: png)
     * @param {number} quality - Quality for lossy formats (0-1)
     * @returns {string} Base64 encoded image
     */
    canvasToBase64(canvas, format = 'png', quality = 0.9) {
        const mimeType = `image/${format}`;
        const dataURL = canvas.toDataURL(mimeType, quality);
        return dataURL.split(',')[1];
    },

    /**
     * Download blob as file
     * @param {Blob} blob - Blob to download
     * @param {string} filename - Filename
     */
    downloadBlob(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
};
