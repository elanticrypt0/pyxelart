/**
 * Debug.js - PyxelArt Debugging Utilities
 *
 * Para usar, abre la consola del navegador (F12) y ejecuta:
 * > PyxelDebug.runAll()
 */

const PyxelDebug = {
    /**
     * Check if all global instances are initialized
     */
    checkGlobals() {
        console.log("🔍 Checking global instances...");
        const checks = {
            'window.app': !!window.app,
            'window.effectsManager': !!window.effectsManager,
            'window.presetManager': !!window.presetManager,
            'window.presetUI': !!window.presetUI,
            'window.comparisonSlider': !!window.comparisonSlider,
            'window.API': !!window.API,
            'window.ImageUtils': !!window.ImageUtils
        };

        Object.entries(checks).forEach(([name, exists]) => {
            console.log(`   ${exists ? '✅' : '❌'} ${name}`);
        });

        return Object.values(checks).every(v => v);
    },

    /**
     * Check if DOM elements exist
     */
    checkDOM() {
        console.log("\n🔍 Checking DOM elements...");
        const elements = [
            'dropzone',
            'fileInput',
            'selectFileBtn',
            'previewCanvas',
            'originalCanvas',
            'effectsSection',
            'pixelartControls',
            'exportSection',
            'loadingIndicator',
            'comparisonContainer'
        ];

        const results = {};
        elements.forEach(id => {
            const el = document.getElementById(id);
            results[id] = !!el;
            console.log(`   ${el ? '✅' : '❌'} #${id}`);
        });

        return Object.values(results).every(v => v);
    },

    /**
     * Check if event listeners are attached to preset buttons
     */
    checkPresetButtons() {
        console.log("\n🔍 Checking preset buttons...");
        const buttons = document.querySelectorAll('.btn-preset');
        console.log(`   Found ${buttons.length} preset buttons`);

        buttons.forEach(btn => {
            const presetId = btn.dataset.preset;
            console.log(`   - ${presetId}: ${btn.textContent.trim()}`);
        });

        return buttons.length === 4;
    },

    /**
     * Check current effect settings
     */
    checkCurrentSettings() {
        console.log("\n🔍 Current effect settings:");
        if (window.effectsManager) {
            const settings = window.effectsManager.getCurrentSettings();
            console.log(`   Active effects: ${settings.effects.join(', ') || 'none'}`);
            console.log(`   Colors: ${settings.colors}`);
            console.log(`   Pixel size: ${settings.pixel_size}`);
            console.log(`   Noise: ${settings.add_noise ? 'enabled' : 'disabled'} (${settings.noise_intensity})`);
            console.log(`   Aberration: ${settings.aberration_intensity}`);
            return true;
        } else {
            console.log("   ❌ effectsManager not initialized");
            return false;
        }
    },

    /**
     * Check if image is loaded
     */
    checkImageLoaded() {
        console.log("\n🔍 Checking loaded image:");
        if (window.effectsManager) {
            const hasOriginal = !!window.effectsManager.currentImageData;
            const hasProcessed = !!window.effectsManager.processedImageData;
            console.log(`   Original image: ${hasOriginal ? '✅' : '❌'}`);
            console.log(`   Processed image: ${hasProcessed ? '✅' : '❌'}`);
            return hasOriginal;
        } else {
            console.log("   ❌ effectsManager not initialized");
            return false;
        }
    },

    /**
     * Test API connectivity
     */
    async testAPI() {
        console.log("\n🔍 Testing API connectivity...");

        try {
            const health = await API.checkHealth();
            console.log(`   ✅ /health: ${health.status}`);
        } catch (error) {
            console.log(`   ❌ /health: ${error.message}`);
            return false;
        }

        try {
            const effects = await API.getEffects();
            console.log(`   ✅ /api/effects: ${Object.keys(effects).length} effects`);
        } catch (error) {
            console.log(`   ❌ /api/effects: ${error.message}`);
            return false;
        }

        try {
            const presets = await API.getPresets();
            console.log(`   ✅ /api/presets: ${presets.presets?.length || 0} presets`);
        } catch (error) {
            console.log(`   ❌ /api/presets: ${error.message}`);
            return false;
        }

        return true;
    },

    /**
     * Test preset application
     */
    testPresetApplication() {
        console.log("\n🔍 Testing preset application...");
        if (!window.presetUI) {
            console.log("   ❌ presetUI not initialized");
            return false;
        }

        console.log("   Attempting to apply '8-bit' preset...");
        try {
            window.presetUI.applyPredefinedPreset('retro_8bit');
            console.log("   ✅ Preset applied successfully");

            // Verify settings changed
            if (window.effectsManager) {
                const settings = window.effectsManager.getCurrentSettings();
                const correct = settings.effects.includes('pixelart') &&
                               settings.colors === 8 &&
                               settings.pixel_size === 6;

                console.log(`   Settings verification: ${correct ? '✅' : '❌'}`);
                console.log(`     - Colors: ${settings.colors} (expected: 8)`);
                console.log(`     - Pixel size: ${settings.pixel_size} (expected: 6)`);

                return correct;
            }
        } catch (error) {
            console.log(`   ❌ Error: ${error.message}`);
            return false;
        }

        return false;
    },

    /**
     * Check localStorage
     */
    checkLocalStorage() {
        console.log("\n🔍 Checking localStorage...");
        try {
            const presets = localStorage.getItem('pyxelart_presets');
            if (presets) {
                const parsed = JSON.parse(presets);
                console.log(`   ✅ Found ${Object.keys(parsed).length} saved presets`);
                Object.values(parsed).forEach(preset => {
                    console.log(`     - ${preset.name} (${preset.id})`);
                });
            } else {
                console.log("   ⚠️ No presets in localStorage");
            }
            return true;
        } catch (error) {
            console.log(`   ❌ Error reading localStorage: ${error.message}`);
            return false;
        }
    },

    /**
     * Run all checks
     */
    async runAll() {
        console.log("═══════════════════════════════════════");
        console.log("   PyxelArt Debug Suite");
        console.log("═══════════════════════════════════════");

        const results = {
            'Globals': this.checkGlobals(),
            'DOM Elements': this.checkDOM(),
            'Preset Buttons': this.checkPresetButtons(),
            'Current Settings': this.checkCurrentSettings(),
            'Image Loaded': this.checkImageLoaded(),
            'localStorage': this.checkLocalStorage(),
            'API': await this.testAPI(),
            'Preset Application': this.testPresetApplication()
        };

        console.log("\n═══════════════════════════════════════");
        console.log("   Summary");
        console.log("═══════════════════════════════════════");

        Object.entries(results).forEach(([name, passed]) => {
            console.log(`${passed ? '✅' : '❌'} ${name}`);
        });

        const passed = Object.values(results).filter(v => v).length;
        const total = Object.keys(results).length;
        console.log(`\n${passed}/${total} checks passed`);

        if (passed < total) {
            console.log("\n⚠️ Some checks failed. See details above.");
            console.log("💡 Tip: Try reloading the page and running again.");
        } else {
            console.log("\n✅ All checks passed! Application should be working.");
        }

        return passed === total;
    },

    /**
     * Quick fixes
     */
    fixes: {
        /**
         * Reinitialize application
         */
        reinit() {
            console.log("🔧 Reinitializing application...");
            window.location.reload();
        },

        /**
         * Clear localStorage
         */
        clearStorage() {
            console.log("🔧 Clearing localStorage...");
            localStorage.removeItem('pyxelart_presets');
            console.log("✅ Done. Reload page to see effect.");
        },

        /**
         * Force preview update
         */
        forcePreview() {
            console.log("🔧 Forcing preview update...");
            if (window.effectsManager) {
                window.effectsManager.previewDelay = 0;
                window.effectsManager.schedulePreview();
                console.log("✅ Preview scheduled");
            } else {
                console.log("❌ effectsManager not initialized");
            }
        },

        /**
         * Test image upload
         */
        async testUpload() {
            console.log("🔧 Creating test image...");

            // Create a simple test image
            const canvas = document.createElement('canvas');
            canvas.width = 200;
            canvas.height = 200;
            const ctx = canvas.getContext('2d');

            // Draw colorful pattern
            for (let i = 0; i < 200; i += 20) {
                ctx.fillStyle = `hsl(${i * 1.8}, 80%, 60%)`;
                ctx.fillRect(i, 0, 20, 200);
            }

            // Convert to blob
            canvas.toBlob(async (blob) => {
                const file = new File([blob], 'test.png', { type: 'image/png' });

                if (window.app) {
                    await window.app.handleFiles([file]);
                    console.log("✅ Test image loaded");
                } else {
                    console.log("❌ App not initialized");
                }
            });
        }
    }
};

// Make available globally
window.PyxelDebug = PyxelDebug;

// Auto-run on load if debug mode is enabled
if (window.location.search.includes('debug')) {
    console.log("🐛 Debug mode enabled (detected ?debug in URL)");
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            PyxelDebug.runAll();
        }, 2000); // Wait 2s for everything to initialize
    });
}

console.log("🐛 PyxelDebug loaded. Run PyxelDebug.runAll() to check everything.");
console.log("💡 Quick fixes available: PyxelDebug.fixes.*");
