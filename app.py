#!/usr/bin/env python3
"""
PyxelArt Flask API
REST API for applying retro effects to images and videos
"""

from flask import Flask, request, send_file, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import io
import base64
import os
import json
from datetime import datetime
from pathlib import Path

# Import PyxelArt effects
from utils import (
    PixelArtEffect,
    ChromaticAberration,
    GlitchEffects,
    BlurEffects,
    PointillistEffect,
    TextureEffects,
    RetroDialog,
    MemoryOptimizer
)

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PRESETS_FOLDER'] = 'presets'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff'}

# Ensure folders exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['PRESETS_FOLDER'], app.config['OUTPUT_FOLDER']]:
    os.makedirs(folder, exist_ok=True)


# ============================================================================
# Helper Functions
# ============================================================================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def decode_base64_image(image_data):
    """Decode base64 image data to PIL Image"""
    # Remove data URL prefix if present
    if ',' in image_data:
        image_data = image_data.split(',')[1]

    # Decode base64
    image_bytes = base64.b64decode(image_data)
    return Image.open(io.BytesIO(image_bytes))


def encode_image_to_base64(img, format='PNG'):
    """Encode PIL Image to base64"""
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    return f"data:image/{format.lower()};base64,{img_base64}"


def apply_effects_to_image(img, effects_config):
    """
    Apply effects to image based on configuration

    Args:
        img: PIL Image
        effects_config: Dict with effect parameters

    Returns:
        Processed PIL Image
    """
    result = img

    # Get effects list
    effects = effects_config.get('effects', [])

    # Apply pixel art effect
    if 'pixelart' in effects:
        colors = effects_config.get('colors', 16)
        pixel_size = effects_config.get('pixel_size', 4)
        add_noise = effects_config.get('add_noise', True)
        noise_intensity = effects_config.get('noise_intensity', 15)

        result = PixelArtEffect.apply(
            result,
            colors=colors,
            pixel_size=pixel_size,
            add_noise=add_noise,
            noise_intensity=noise_intensity
        )

    # Apply chromatic aberration
    if 'chromatic' in effects:
        intensity = effects_config.get('aberration_intensity', 1.0)
        red_shift = effects_config.get('red_shift', (2, 0))
        green_shift = effects_config.get('green_shift', (0, 0))
        blue_shift = effects_config.get('blue_shift', (-2, 0))
        lens_effect = effects_config.get('lens_effect', False)

        result = ChromaticAberration.apply(
            result,
            intensity=intensity,
            red_shift=red_shift,
            green_shift=green_shift,
            blue_shift=blue_shift,
            lens_effect=lens_effect
        )

    # Apply glitch effects
    if 'glitch_blocks' in effects:
        intensity = effects_config.get('glitch_intensity', 10)
        result = GlitchEffects.glitch_blocks(result, intensity=intensity)

    if 'glitch_horizontal' in effects:
        intensity = effects_config.get('glitch_intensity', 5)
        result = GlitchEffects.glitch_horizontal_shift(result, intensity=intensity)

    if 'glitch_scanlines' in effects:
        intensity = effects_config.get('scanline_intensity', 0.1)
        result = GlitchEffects.glitch_scanlines(result, intensity=intensity)

    # Apply blur effects
    if 'blur_gaussian' in effects:
        radius = effects_config.get('blur_radius', 2.0)
        result = BlurEffects.gaussian_blur(result, radius=radius)

    if 'blur_motion' in effects:
        angle = effects_config.get('blur_angle', 0)
        distance = effects_config.get('blur_distance', 5)
        result = BlurEffects.motion_blur(result, angle=angle, distance=distance)

    if 'light_trail' in effects:
        intensity = effects_config.get('trail_intensity', 50)
        result = BlurEffects.light_trail(result, intensity=intensity)

    # Apply artistic effects
    if 'pointillist' in effects:
        dot_size = effects_config.get('dot_size', 6)
        result = PointillistEffect.apply(result, dot_size=dot_size)

    if 'texture' in effects:
        intensity = effects_config.get('texture_intensity', 50)
        result = TextureEffects.canvas_texture(result, intensity=intensity)

    # Apply dialog
    if 'dialog' in effects:
        text = effects_config.get('dialog_text', 'RETRO')
        pixel_size = effects_config.get('pixel_size', 4)
        result = RetroDialog.add_dialog(result, text=text, pixel_size=pixel_size)

    return result


# ============================================================================
# Routes - Main
# ============================================================================

@app.route('/')
def index():
    """Serve main page"""
    return jsonify({
        'message': 'PyxelArt API',
        'version': '1.0.0',
        'endpoints': {
            'preview': '/api/preview',
            'apply_effects': '/api/apply-effects',
            'export': '/api/export',
            'presets': '/api/presets',
            'effects': '/api/effects'
        }
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


# ============================================================================
# Routes - Effects
# ============================================================================

@app.route('/api/effects', methods=['GET'])
def get_effects():
    """Get list of available effects"""
    effects = {
        'pixelart': {
            'name': 'Pixel Art',
            'description': 'Retro pixel art effect with color reduction',
            'parameters': {
                'colors': {'type': 'int', 'default': 16, 'range': [4, 256]},
                'pixel_size': {'type': 'int', 'default': 4, 'range': [1, 20]},
                'add_noise': {'type': 'bool', 'default': True},
                'noise_intensity': {'type': 'int', 'default': 15, 'range': [1, 50]}
            }
        },
        'chromatic': {
            'name': 'Chromatic Aberration',
            'description': 'RGB channel shift effect',
            'parameters': {
                'aberration_intensity': {'type': 'float', 'default': 1.0, 'range': [0.1, 5.0]},
                'lens_effect': {'type': 'bool', 'default': False}
            }
        },
        'glitch_blocks': {
            'name': 'Glitch Blocks',
            'description': 'Random block displacement glitch',
            'parameters': {
                'glitch_intensity': {'type': 'int', 'default': 10, 'range': [1, 50]}
            }
        },
        'glitch_horizontal': {
            'name': 'Horizontal Glitch',
            'description': 'Horizontal strip shift glitch',
            'parameters': {
                'glitch_intensity': {'type': 'int', 'default': 5, 'range': [1, 20]}
            }
        },
        'glitch_scanlines': {
            'name': 'Scanlines',
            'description': 'CRT scanline effect',
            'parameters': {
                'scanline_intensity': {'type': 'float', 'default': 0.1, 'range': [0.0, 1.0]}
            }
        },
        'blur_gaussian': {
            'name': 'Gaussian Blur',
            'description': 'Smooth gaussian blur',
            'parameters': {
                'blur_radius': {'type': 'float', 'default': 2.0, 'range': [0.5, 10.0]}
            }
        },
        'light_trail': {
            'name': 'Light Trail',
            'description': 'Moving lights effect',
            'parameters': {
                'trail_intensity': {'type': 'int', 'default': 50, 'range': [0, 100]}
            }
        },
        'pointillist': {
            'name': 'Pointillist',
            'description': 'Pointillist/stippling effect',
            'parameters': {
                'dot_size': {'type': 'int', 'default': 6, 'range': [2, 20]}
            }
        },
        'texture': {
            'name': 'Canvas Texture',
            'description': 'Canvas texture overlay',
            'parameters': {
                'texture_intensity': {'type': 'int', 'default': 50, 'range': [0, 100]}
            }
        },
        'dialog': {
            'name': 'Retro Dialog',
            'description': 'Add retro dialog box',
            'parameters': {
                'dialog_text': {'type': 'string', 'default': 'RETRO'},
                'pixel_size': {'type': 'int', 'default': 4, 'range': [2, 10]}
            }
        }
    }

    return jsonify(effects)


@app.route('/api/preview', methods=['POST'])
def preview():
    """
    Generate preview with effects (low resolution for speed)

    Request JSON:
    {
        "imageData": "base64 encoded image",
        "effects": ["pixelart", "chromatic"],
        "colors": 16,
        "pixel_size": 4,
        ...
    }

    Response JSON:
    {
        "preview": "base64 encoded preview image",
        "width": 800,
        "height": 600
    }
    """
    try:
        data = request.json

        if not data or 'imageData' not in data:
            return jsonify({'error': 'No image data provided'}), 400

        # Decode image
        img = decode_base64_image(data['imageData'])

        # Create preview (max 800px for speed)
        preview_img = MemoryOptimizer.create_preview(img, max_dimension=800)

        # Apply effects
        result = apply_effects_to_image(preview_img, data)

        # Encode result
        preview_base64 = encode_image_to_base64(result, format='PNG')

        return jsonify({
            'preview': preview_base64,
            'width': result.width,
            'height': result.height
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/apply-effects', methods=['POST'])
def apply_effects():
    """
    Apply effects to full resolution image

    Request JSON:
    {
        "imageData": "base64 encoded image",
        "effects": ["pixelart", "chromatic"],
        "colors": 16,
        "pixel_size": 4,
        ...
    }

    Response JSON:
    {
        "result": "base64 encoded result image",
        "width": 1920,
        "height": 1080
    }
    """
    try:
        data = request.json

        if not data or 'imageData' not in data:
            return jsonify({'error': 'No image data provided'}), 400

        # Decode image
        img = decode_base64_image(data['imageData'])

        # Apply effects
        result = apply_effects_to_image(img, data)

        # Encode result
        result_base64 = encode_image_to_base64(result, format='PNG')

        return jsonify({
            'result': result_base64,
            'width': result.width,
            'height': result.height
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Routes - Presets
# ============================================================================

@app.route('/api/presets', methods=['GET'])
def get_presets():
    """Get all saved presets"""
    try:
        presets_dir = Path(app.config['PRESETS_FOLDER'])
        presets = []

        for preset_file in presets_dir.glob('*.json'):
            with open(preset_file, 'r') as f:
                preset_data = json.load(f)
                preset_data['id'] = preset_file.stem
                presets.append(preset_data)

        return jsonify({'presets': presets})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/presets/<preset_id>', methods=['GET'])
def get_preset(preset_id):
    """Get specific preset by ID"""
    try:
        preset_file = Path(app.config['PRESETS_FOLDER']) / f"{preset_id}.json"

        if not preset_file.exists():
            return jsonify({'error': 'Preset not found'}), 404

        with open(preset_file, 'r') as f:
            preset = json.load(f)
            preset['id'] = preset_id

        return jsonify(preset)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/presets', methods=['POST'])
def create_preset():
    """
    Create new preset

    Request JSON:
    {
        "name": "Retro CRT",
        "effects": ["pixelart", "chromatic"],
        "params": {
            "colors": 16,
            "pixel_size": 4,
            "aberration_intensity": 1.5
        },
        "output": {
            "format": "png",
            "quality": 90
        }
    }

    Response JSON:
    {
        "id": "preset_id",
        "message": "Preset created successfully"
    }
    """
    try:
        data = request.json

        if not data or 'name' not in data:
            return jsonify({'error': 'Preset name is required'}), 400

        # Generate preset ID from name and timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        safe_name = secure_filename(data['name'].lower().replace(' ', '_'))
        preset_id = f"{safe_name}_{timestamp}"

        # Create preset object
        preset = {
            'name': data['name'],
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'effects': data.get('effects', []),
            'params': data.get('params', {}),
            'output': data.get('output', {'format': 'png', 'quality': 90})
        }

        # Save to file
        preset_file = Path(app.config['PRESETS_FOLDER']) / f"{preset_id}.json"
        with open(preset_file, 'w') as f:
            json.dump(preset, f, indent=2)

        return jsonify({
            'id': preset_id,
            'message': 'Preset created successfully'
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/presets/<preset_id>', methods=['DELETE'])
def delete_preset(preset_id):
    """Delete preset by ID"""
    try:
        preset_file = Path(app.config['PRESETS_FOLDER']) / f"{preset_id}.json"

        if not preset_file.exists():
            return jsonify({'error': 'Preset not found'}), 404

        preset_file.unlink()

        return jsonify({'message': 'Preset deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Routes - Export
# ============================================================================

@app.route('/api/export', methods=['POST'])
def export_image():
    """
    Export image in specific format

    Request JSON:
    {
        "imageData": "base64 encoded image",
        "format": "png|jpg|webp|tiff",
        "quality": 90,
        "dpi": 300,
        "filename": "output.png"
    }

    Response:
        File download
    """
    try:
        data = request.json

        if not data or 'imageData' not in data:
            return jsonify({'error': 'No image data provided'}), 400

        # Decode image
        img = decode_base64_image(data['imageData'])

        # Get export parameters
        export_format = data.get('format', 'png').upper()
        quality = data.get('quality', 90)
        dpi = data.get('dpi', 300)
        filename = data.get('filename', f'pyxelart_export.{export_format.lower()}')

        # Prepare output buffer
        output = io.BytesIO()

        # Save with format-specific parameters
        save_params = {}

        if export_format == 'JPG' or export_format == 'JPEG':
            # Convert to RGB (JPG doesn't support transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img

            save_params = {'quality': quality, 'optimize': True, 'dpi': (dpi, dpi)}
            img.save(output, format='JPEG', **save_params)
            mimetype = 'image/jpeg'

        elif export_format == 'PNG':
            save_params = {'optimize': True, 'dpi': (dpi, dpi)}
            img.save(output, format='PNG', **save_params)
            mimetype = 'image/png'

        elif export_format == 'WEBP':
            save_params = {'quality': quality, 'method': 6}
            img.save(output, format='WEBP', **save_params)
            mimetype = 'image/webp'

        elif export_format == 'TIFF':
            save_params = {'compression': 'tiff_adobe_deflate', 'dpi': (dpi, dpi)}
            img.save(output, format='TIFF', **save_params)
            mimetype = 'image/tiff'

        else:
            return jsonify({'error': f'Unsupported format: {export_format}'}), 400

        output.seek(0)

        return send_file(
            output,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/batch-process', methods=['POST'])
def batch_process():
    """
    Process multiple images with same preset

    Request JSON:
    {
        "preset_id": "retro_crt_123",
        "images": ["base64_img1", "base64_img2", ...]
    }

    Response JSON:
    {
        "results": ["base64_result1", "base64_result2", ...],
        "count": 2
    }
    """
    try:
        data = request.json

        if not data or 'images' not in data:
            return jsonify({'error': 'No images provided'}), 400

        # Get preset if specified
        preset_config = {}
        if 'preset_id' in data:
            preset_file = Path(app.config['PRESETS_FOLDER']) / f"{data['preset_id']}.json"
            if preset_file.exists():
                with open(preset_file, 'r') as f:
                    preset = json.load(f)
                    preset_config = {
                        'effects': preset.get('effects', []),
                        **preset.get('params', {})
                    }
        else:
            # Use provided config
            preset_config = data.get('config', {})

        # Process all images
        results = []
        for img_data in data['images']:
            img = decode_base64_image(img_data)
            result = apply_effects_to_image(img, preset_config)
            result_base64 = encode_image_to_base64(result, format='PNG')
            results.append(result_base64)

        return jsonify({
            'results': results,
            'count': len(results)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(413)
def file_too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large (max 50MB)'}), 413


@app.errorhandler(404)
def not_found(e):
    """Handle not found error"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server error"""
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    print("🎨 PyxelArt API Server")
    print("📡 Starting on http://localhost:5000")
    print("📚 API endpoints available at /")
    app.run(debug=True, host='0.0.0.0', port=5000)
