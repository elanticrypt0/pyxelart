# PyxelArt REST API Documentation

Complete REST API documentation for PyxelArt web application.

## Base URL

```
http://localhost:5000
```

## Table of Contents
- [General](#general)
- [Effects Endpoints](#effects-endpoints)
- [Presets Endpoints](#presets-endpoints)
- [Export Endpoints](#export-endpoints)
- [Error Handling](#error-handling)
- [Examples](#examples)

---

## General

### Health Check

Check API status.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-03T06:00:00.000000"
}
```

### API Info

Get available endpoints.

**Endpoint:** `GET /`

**Response:**
```json
{
  "message": "PyxelArt API",
  "version": "1.0.0",
  "endpoints": {
    "preview": "/api/preview",
    "apply_effects": "/api/apply-effects",
    "export": "/api/export",
    "presets": "/api/presets",
    "effects": "/api/effects"
  }
}
```

---

## Effects Endpoints

### Get Available Effects

List all available effects with parameters.

**Endpoint:** `GET /api/effects`

**Response:**
```json
{
  "pixelart": {
    "name": "Pixel Art",
    "description": "Retro pixel art effect with color reduction",
    "parameters": {
      "colors": {"type": "int", "default": 16, "range": [4, 256]},
      "pixel_size": {"type": "int", "default": 4, "range": [1, 20]},
      "add_noise": {"type": "bool", "default": true},
      "noise_intensity": {"type": "int", "default": 15, "range": [1, 50]}
    }
  },
  ...
}
```

### Generate Preview

Generate low-resolution preview (fast).

**Endpoint:** `POST /api/preview`

**Request:**
```json
{
  "imageData": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "effects": ["pixelart", "chromatic"],
  "colors": 16,
  "pixel_size": 4,
  "aberration_intensity": 1.5
}
```

**Response:**
```json
{
  "preview": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "width": 800,
  "height": 600
}
```

**Parameters:**
- `imageData` (string, required): Base64 encoded image
- `effects` (array, required): List of effects to apply
- Additional parameters depend on effects selected

### Apply Effects

Apply effects to full resolution image.

**Endpoint:** `POST /api/apply-effects`

**Request:**
```json
{
  "imageData": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "effects": ["pixelart", "chromatic", "glitch_scanlines"],
  "colors": 16,
  "pixel_size": 4,
  "aberration_intensity": 1.0,
  "scanline_intensity": 0.15
}
```

**Response:**
```json
{
  "result": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "width": 1920,
  "height": 1080
}
```

---

## Presets Endpoints

### Get All Presets

List all saved presets.

**Endpoint:** `GET /api/presets`

**Response:**
```json
{
  "presets": [
    {
      "id": "retro_8bit",
      "name": "Retro 8-bit",
      "version": "1.0",
      "created_at": "2025-10-03T06:00:00",
      "effects": ["pixelart"],
      "params": {
        "colors": 8,
        "pixel_size": 6
      },
      "output": {
        "format": "png",
        "quality": 95
      }
    },
    ...
  ]
}
```

### Get Preset by ID

Get specific preset details.

**Endpoint:** `GET /api/presets/<preset_id>`

**Example:** `GET /api/presets/retro_8bit`

**Response:**
```json
{
  "id": "retro_8bit",
  "name": "Retro 8-bit",
  "version": "1.0",
  "created_at": "2025-10-03T06:00:00",
  "effects": ["pixelart"],
  "params": {
    "colors": 8,
    "pixel_size": 6,
    "add_noise": true,
    "noise_intensity": 20
  },
  "output": {
    "format": "png",
    "quality": 95
  }
}
```

### Create Preset

Save new preset.

**Endpoint:** `POST /api/presets`

**Request:**
```json
{
  "name": "My Custom Preset",
  "effects": ["pixelart", "chromatic"],
  "params": {
    "colors": 16,
    "pixel_size": 4,
    "aberration_intensity": 1.5
  },
  "output": {
    "format": "webp",
    "quality": 90
  }
}
```

**Response:**
```json
{
  "id": "my_custom_preset_20251003060000",
  "message": "Preset created successfully"
}
```

### Delete Preset

Delete preset by ID.

**Endpoint:** `DELETE /api/presets/<preset_id>`

**Example:** `DELETE /api/presets/my_custom_preset_20251003060000`

**Response:**
```json
{
  "message": "Preset deleted successfully"
}
```

---

## Export Endpoints

### Export Image

Export processed image in specific format.

**Endpoint:** `POST /api/export`

**Request:**
```json
{
  "imageData": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "format": "webp",
  "quality": 90,
  "dpi": 300,
  "filename": "my_retro_image.webp"
}
```

**Response:**
- File download (image/webp, image/png, image/jpeg, image/tiff)

**Supported Formats:**
- `png` - PNG with optimization
- `jpg` or `jpeg` - JPEG with quality control
- `webp` - WebP with quality control
- `tiff` - TIFF with LZW compression and DPI

**Parameters:**
- `imageData` (string, required): Base64 encoded image
- `format` (string, default: "png"): Output format
- `quality` (int, default: 90): Quality for JPG/WebP (1-100)
- `dpi` (int, default: 300): DPI for PNG/TIFF
- `filename` (string, optional): Output filename

### Batch Process

Process multiple images with same preset.

**Endpoint:** `POST /api/batch-process`

**Request:**
```json
{
  "preset_id": "retro_8bit",
  "images": [
    "data:image/png;base64,iVBORw0...",
    "data:image/png;base64,iVBORw0...",
    "data:image/png;base64,iVBORw0..."
  ]
}
```

**Alternative (without preset):**
```json
{
  "config": {
    "effects": ["pixelart"],
    "colors": 16,
    "pixel_size": 4
  },
  "images": [
    "data:image/png;base64,iVBORw0...",
    "data:image/png;base64,iVBORw0..."
  ]
}
```

**Response:**
```json
{
  "results": [
    "data:image/png;base64,iVBORw0...",
    "data:image/png;base64,iVBORw0...",
    "data:image/png;base64,iVBORw0..."
  ],
  "count": 3
}
```

---

## Error Handling

All endpoints return errors in consistent format:

```json
{
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `201` - Created (presets)
- `400` - Bad Request (missing/invalid parameters)
- `404` - Not Found (preset not found)
- `413` - Payload Too Large (file > 50MB)
- `500` - Internal Server Error

---

## Examples

### Example 1: Apply Pixel Art Effect

```javascript
// JavaScript/Fetch example
const response = await fetch('http://localhost:5000/api/apply-effects', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    imageData: 'data:image/png;base64,iVBORw0...',
    effects: ['pixelart'],
    colors: 16,
    pixel_size: 4
  })
});

const data = await response.json();
console.log('Processed image:', data.result);
```

```python
# Python example
import requests
import base64

# Read and encode image
with open('input.png', 'rb') as f:
    img_data = base64.b64encode(f.read()).decode('utf-8')

# Apply effects
response = requests.post('http://localhost:5000/api/apply-effects', json={
    'imageData': f'data:image/png;base64,{img_data}',
    'effects': ['pixelart'],
    'colors': 16,
    'pixel_size': 4
})

result = response.json()
print('Processed:', result['width'], 'x', result['height'])
```

### Example 2: Use Preset

```javascript
// Load preset and apply to image
const preset = await fetch('http://localhost:5000/api/presets/retro_8bit')
  .then(r => r.json());

const response = await fetch('http://localhost:5000/api/apply-effects', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    imageData: 'data:image/png;base64,iVBORw0...',
    effects: preset.effects,
    ...preset.params
  })
});
```

### Example 3: Create and Export

```javascript
// Apply effects and export as WebP
const applyResponse = await fetch('http://localhost:5000/api/apply-effects', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    imageData: 'data:image/png;base64,iVBORw0...',
    effects: ['pixelart', 'chromatic'],
    colors: 16,
    aberration_intensity: 1.5
  })
});

const { result } = await applyResponse.json();

// Export as WebP
const exportResponse = await fetch('http://localhost:5000/api/export', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    imageData: result,
    format: 'webp',
    quality: 90,
    filename: 'retro_image.webp'
  })
});

const blob = await exportResponse.blob();
// Download or save blob
```

### Example 4: Batch Processing

```javascript
// Process multiple images with same preset
const images = [
  'data:image/png;base64,img1...',
  'data:image/png;base64,img2...',
  'data:image/png;base64,img3...'
];

const response = await fetch('http://localhost:5000/api/batch-process', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    preset_id: 'retro_16bit',
    images: images
  })
});

const { results, count } = await response.json();
console.log(`Processed ${count} images`);
```

### Example 5: Create Custom Preset

```javascript
// Create and save custom preset
const response = await fetch('http://localhost:5000/api/presets', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'CRT Monitor Effect',
    effects: ['pixelart', 'chromatic', 'glitch_scanlines'],
    params: {
      colors: 64,
      pixel_size: 2,
      aberration_intensity: 1.0,
      scanline_intensity: 0.15
    },
    output: {
      format: 'png',
      quality: 90
    }
  })
});

const { id } = await response.json();
console.log('Created preset ID:', id);
```

---

## Effect Parameters Reference

### Pixel Art
- `colors` (int): Number of colors (4-256, default: 16)
- `pixel_size` (int): Pixelation level (1-20, default: 4)
- `add_noise` (bool): Add retro noise (default: true)
- `noise_intensity` (int): Noise amount (1-50, default: 15)

### Chromatic Aberration
- `aberration_intensity` (float): Effect intensity (0.1-5.0, default: 1.0)
- `red_shift` (array): [x, y] shift for red channel (default: [2, 0])
- `green_shift` (array): [x, y] shift for green channel (default: [0, 0])
- `blue_shift` (array): [x, y] shift for blue channel (default: [-2, 0])
- `lens_effect` (bool): Apply lens distortion (default: false)

### Glitch Effects
- `glitch_intensity` (int): Blocks/strips intensity (1-50, default: 10)
- `scanline_intensity` (float): Scanline density (0.0-1.0, default: 0.1)

### Blur Effects
- `blur_radius` (float): Gaussian blur radius (0.5-10.0, default: 2.0)
- `blur_angle` (int): Motion blur angle in degrees (default: 0)
- `blur_distance` (int): Motion blur distance (default: 5)
- `trail_intensity` (int): Light trail effect (0-100, default: 50)

### Artistic Effects
- `dot_size` (int): Pointillist dot size (2-20, default: 6)
- `texture_intensity` (int): Canvas texture (0-100, default: 50)

### Dialog
- `dialog_text` (string): Text to display (default: "RETRO")

---

## Running the API

```bash
# Install dependencies
pip install flask pillow

# Run server
python app.py

# Server starts on http://localhost:5000
```

---

## Notes

- Maximum file size: 50MB
- Preview endpoint uses max 800px dimension for speed
- All base64 images should include data URL prefix: `data:image/png;base64,`
- TIFF export preserves DPI information
- JPG export converts RGBA to RGB (white background)
- Batch processing returns results in same order as input
