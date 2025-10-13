/**
 * Presets.js - PyxelArt Preset Management System
 * Adapted from mynegatives preset system
 */

class PresetManager {
    constructor() {
        this.presets = {};
        this.currentPreset = null;
        this.localStorageKey = 'pyxelart_presets';
        this.loadPresetsFromLocalStorage();
    }

    /**
     * Load presets from localStorage
     */
    loadPresetsFromLocalStorage() {
        try {
            const stored = localStorage.getItem(this.localStorageKey);
            if (stored) {
                this.presets = JSON.parse(stored);
            }
        } catch (error) {
            console.error('Error loading presets from localStorage:', error);
            this.presets = {};
        }
    }

    /**
     * Save presets to localStorage
     */
    savePresetsToLocalStorage() {
        try {
            localStorage.setItem(this.localStorageKey, JSON.stringify(this.presets));
        } catch (error) {
            console.error('Error saving presets to localStorage:', error);
        }
    }

    /**
     * Create preset from current settings
     * @param {string} name - Preset name
     * @param {object} params - Effect parameters
     * @returns {object} Created preset
     */
    createPreset(name, params) {
        const preset = {
            id: this.generatePresetId(),
            name: name,
            version: '1.0',
            created_at: new Date().toISOString(),
            effects: params.effects || [],
            params: { ...params }
        };

        // Remove effects from params to avoid duplication
        delete preset.params.effects;

        this.presets[preset.id] = preset;
        this.savePresetsToLocalStorage();

        return preset;
    }

    /**
     * Save preset to backend
     * @param {object} preset - Preset object
     * @returns {Promise}
     */
    async savePresetToBackend(preset) {
        try {
            const result = await API.savePreset(preset);
            return result;
        } catch (error) {
            console.error('Error saving preset to backend:', error);
            throw error;
        }
    }

    /**
     * Load preset
     * @param {string} presetId - Preset ID
     * @returns {object} Preset object
     */
    loadPreset(presetId) {
        if (this.presets[presetId]) {
            this.currentPreset = this.presets[presetId];
            return this.currentPreset;
        }
        throw new Error(`Preset ${presetId} not found`);
    }

    /**
     * Load presets from backend
     * @returns {Promise<Array>}
     */
    async loadPresetsFromBackend() {
        try {
            const response = await API.getPresets();
            if (response.presets && Array.isArray(response.presets)) {
                // Convert array to object keyed by ID
                response.presets.forEach(preset => {
                    this.presets[preset.id] = preset;
                });
                this.savePresetsToLocalStorage();
                return response.presets;
            }
            return [];
        } catch (error) {
            console.error('Error loading presets from backend:', error);
            throw error;
        }
    }

    /**
     * Delete preset
     * @param {string} presetId - Preset ID
     */
    deletePreset(presetId) {
        if (this.presets[presetId]) {
            delete this.presets[presetId];
            this.savePresetsToLocalStorage();

            if (this.currentPreset && this.currentPreset.id === presetId) {
                this.currentPreset = null;
            }
        }
    }

    /**
     * Delete preset from backend
     * @param {string} presetId - Preset ID
     * @returns {Promise}
     */
    async deletePresetFromBackend(presetId) {
        try {
            await API.deletePreset(presetId);
            this.deletePreset(presetId);
        } catch (error) {
            console.error('Error deleting preset from backend:', error);
            throw error;
        }
    }

    /**
     * Rename preset
     * @param {string} presetId - Preset ID
     * @param {string} newName - New name
     */
    renamePreset(presetId, newName) {
        if (this.presets[presetId]) {
            this.presets[presetId].name = newName;
            this.savePresetsToLocalStorage();
        }
    }

    /**
     * Get all presets
     * @returns {Array} Array of presets
     */
    getAllPresets() {
        return Object.values(this.presets);
    }

    /**
     * Export preset to JSON file
     * @param {string} presetId - Preset ID
     */
    exportPresetToFile(presetId) {
        const preset = this.presets[presetId];
        if (!preset) {
            throw new Error(`Preset ${presetId} not found`);
        }

        const json = JSON.stringify(preset, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const filename = `${preset.name.replace(/\s+/g, '_')}.json`;

        ImageUtils.downloadBlob(blob, filename);
    }

    /**
     * Import preset from JSON file
     * @param {File} file - JSON file
     * @returns {Promise<object>} Imported preset
     */
    async importPresetFromFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();

            reader.onload = (e) => {
                try {
                    const preset = JSON.parse(e.target.result);

                    // Validate preset structure
                    if (!preset.name || !preset.effects) {
                        throw new Error('Invalid preset format');
                    }

                    // Generate new ID to avoid conflicts
                    preset.id = this.generatePresetId();
                    preset.created_at = new Date().toISOString();

                    this.presets[preset.id] = preset;
                    this.savePresetsToLocalStorage();

                    resolve(preset);
                } catch (error) {
                    reject(error);
                }
            };

            reader.onerror = () => reject(new Error('Error reading file'));
            reader.readAsText(file);
        });
    }

    /**
     * Generate unique preset ID
     * @returns {string} Unique ID
     */
    generatePresetId() {
        return `preset_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Apply preset to parameters
     * @param {object} preset - Preset to apply
     * @returns {object} Parameters object
     */
    applyPreset(preset) {
        return {
            effects: preset.effects || [],
            ...preset.params
        };
    }
}

/**
 * Predefined PyxelArt presets
 */
const PREDEFINED_PRESETS = {
    retro_8bit: {
        id: 'retro_8bit',
        name: '8-bit Retro',
        version: '1.0',
        effects: ['pixelart'],
        params: {
            colors: 8,
            pixel_size: 6,
            add_noise: true,
            noise_intensity: 20
        }
    },
    retro_16bit: {
        id: 'retro_16bit',
        name: '16-bit Retro',
        version: '1.0',
        effects: ['pixelart'],
        params: {
            colors: 16,
            pixel_size: 4,
            add_noise: true,
            noise_intensity: 15
        }
    },
    crt_monitor: {
        id: 'crt_monitor',
        name: 'CRT Monitor',
        version: '1.0',
        effects: ['pixelart', 'chromatic', 'glitch_scanlines'],
        params: {
            colors: 64,
            pixel_size: 2,
            aberration_intensity: 1.0,
            scanline_intensity: 0.15,
            add_noise: true,
            noise_intensity: 10
        }
    },
    game_over: {
        id: 'game_over',
        name: 'Game Over',
        version: '1.0',
        effects: ['pixelart', 'chromatic', 'dialog'],
        params: {
            colors: 16,
            pixel_size: 4,
            aberration_intensity: 0.5,
            dialog_text: 'GAME OVER',
            add_noise: true,
            noise_intensity: 15
        }
    }
};

/**
 * UI Manager for Presets
 */
class PresetUI {
    constructor(presetManager) {
        this.presetManager = presetManager;
        this.presetsListElement = null;
        this.init();
    }

    init() {
        this.presetsListElement = document.getElementById('savedPresetsList');
        this.setupEventListeners();
        this.loadPredefinedPresets();
        this.renderPresetsList();
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Save preset button
        const saveBtn = document.getElementById('savePreset');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.handleSavePreset());
        }

        // Load preset button
        const loadBtn = document.getElementById('loadPreset');
        const presetInput = document.getElementById('presetInput');
        if (loadBtn && presetInput) {
            loadBtn.addEventListener('click', () => presetInput.click());
            presetInput.addEventListener('change', (e) => this.handleLoadPresetFile(e));
        }

        // Predefined preset buttons
        document.querySelectorAll('.btn-preset').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const presetId = e.target.dataset.preset;
                this.applyPredefinedPreset(presetId);
            });
        });
    }

    /**
     * Load predefined presets into manager
     */
    loadPredefinedPresets() {
        Object.values(PREDEFINED_PRESETS).forEach(preset => {
            if (!this.presetManager.presets[preset.id]) {
                this.presetManager.presets[preset.id] = preset;
            }
        });
        this.presetManager.savePresetsToLocalStorage();
    }

    /**
     * Handle save preset
     */
    async handleSavePreset() {
        const name = prompt('Nombre del preset:');
        if (!name) return;

        try {
            // Get current settings from UI
            const params = window.effectsManager ? window.effectsManager.getCurrentSettings() : {};

            const preset = this.presetManager.createPreset(name, params);

            // Optionally save to backend
            try {
                await this.presetManager.savePresetToBackend(preset);
                console.log('Preset saved to backend');
            } catch (error) {
                console.warn('Could not save to backend, saved locally only');
            }

            this.renderPresetsList();
            alert(`Preset "${name}" guardado correctamente`);
        } catch (error) {
            console.error('Error saving preset:', error);
            alert('Error al guardar preset');
        }
    }

    /**
     * Handle load preset from file
     */
    async handleLoadPresetFile(event) {
        const file = event.target.files[0];
        if (!file) return;

        try {
            const preset = await this.presetManager.importPresetFromFile(file);
            this.renderPresetsList();
            this.applyPreset(preset);
            alert(`Preset "${preset.name}" cargado correctamente`);
        } catch (error) {
            console.error('Error loading preset:', error);
            alert('Error al cargar preset. Verifica que el archivo sea válido.');
        }

        // Reset input
        event.target.value = '';
    }

    /**
     * Apply predefined preset
     */
    applyPredefinedPreset(presetId) {
        const preset = PREDEFINED_PRESETS[presetId];
        if (preset) {
            this.applyPreset(preset);
        }
    }

    /**
     * Apply preset to UI
     */
    applyPreset(preset) {
        if (window.effectsManager) {
            window.effectsManager.applyPresetSettings(preset);
        }
    }

    /**
     * Render presets list
     */
    renderPresetsList() {
        if (!this.presetsListElement) return;

        const presets = this.presetManager.getAllPresets()
            .filter(p => !PREDEFINED_PRESETS[p.id]); // Exclude predefined

        if (presets.length === 0) {
            this.presetsListElement.innerHTML = '<p class="empty-message">No hay presets guardados</p>';
            return;
        }

        this.presetsListElement.innerHTML = presets.map(preset => `
            <div class="preset-item" data-preset-id="${preset.id}">
                <span class="preset-item-name">${preset.name}</span>
                <div class="preset-item-actions">
                    <button class="preset-item-btn" onclick="presetUI.handleLoadPreset('${preset.id}')" title="Cargar">
                        📂
                    </button>
                    <button class="preset-item-btn" onclick="presetUI.handleExportPreset('${preset.id}')" title="Exportar">
                        💾
                    </button>
                    <button class="preset-item-btn" onclick="presetUI.handleDeletePreset('${preset.id}')" title="Eliminar">
                        🗑️
                    </button>
                </div>
            </div>
        `).join('');
    }

    /**
     * Handle load preset
     */
    handleLoadPreset(presetId) {
        try {
            const preset = this.presetManager.loadPreset(presetId);
            this.applyPreset(preset);
        } catch (error) {
            console.error('Error loading preset:', error);
            alert('Error al cargar preset');
        }
    }

    /**
     * Handle export preset
     */
    handleExportPreset(presetId) {
        try {
            this.presetManager.exportPresetToFile(presetId);
        } catch (error) {
            console.error('Error exporting preset:', error);
            alert('Error al exportar preset');
        }
    }

    /**
     * Handle delete preset
     */
    async handleDeletePreset(presetId) {
        if (!confirm('¿Eliminar este preset?')) return;

        try {
            // Try to delete from backend
            try {
                await this.presetManager.deletePresetFromBackend(presetId);
            } catch (error) {
                // If backend fails, still delete locally
                this.presetManager.deletePreset(presetId);
            }

            this.renderPresetsList();
        } catch (error) {
            console.error('Error deleting preset:', error);
            alert('Error al eliminar preset');
        }
    }
}

// Global instances (will be initialized in app.js)
let presetManager;
let presetUI;
