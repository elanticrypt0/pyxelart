# PyxelArt Utils API Documentation

Complete API documentation for PyxelArt utilities modules.

## Table of Contents
- [Effects Core](#effects-core)
- [Sprite Utils](#sprite-utils)
- [Parallel Utils](#parallel-utils)

---

## Effects Core

### PixelArtEffect
Main pixel art effect with color reduction and pixelation.

```python
from utils import PixelArtEffect

# Apply pixel art effect
result = PixelArtEffect.apply(
    img,                    # PIL Image object
    colors=16,             # Number of colors (default: 16)
    pixel_size=4,          # Pixelation level (default: 4)
    add_noise=True,        # Add retro noise (default: True)
    noise_intensity=15     # Noise intensity (default: 15)
)
```

### ChromaticAberration
Chromatic aberration and RGB channel shift effects.

```python
from utils import ChromaticAberration

result = ChromaticAberration.apply(
    img,
    intensity=1.0,                    # Overall intensity multiplier
    red_shift=(2, 0),                # (x, y) shift for red channel
    green_shift=(0, 0),              # (x, y) shift for green channel
    blue_shift=(-2, 0),              # (x, y) shift for blue channel
    lens_effect=False,               # Apply lens distortion
    lens_center=None,                # Center for lens effect
    lens_falloff='quadratic',        # 'quadratic' or 'linear'
    edge_mode='transparent'          # 'transparent', 'black', 'white', 'clamp'
)
```

### GlitchEffects
Various glitch and distortion effects.

```python
from utils import GlitchEffects

# Block glitch
result = GlitchEffects.glitch_blocks(
    img,
    intensity=10,           # Number of blocks to displace
    block_size_min=10,     # Minimum block size
    block_size_max=50,     # Maximum block size
    seed=None              # Random seed for reproducibility
)

# Horizontal shift glitch
result = GlitchEffects.glitch_horizontal_shift(
    img,
    intensity=5,           # Number of strips to shift
    shift_height_min=5,    # Minimum strip height
    shift_height_max=20,   # Maximum strip height
    max_offset=50,         # Maximum horizontal offset
    seed=None
)

# Scanline glitch
result = GlitchEffects.glitch_scanlines(
    img,
    intensity=0.1,                  # Line density (0.0 to 1.0)
    line_height=1,                  # Line thickness
    line_color=(0, 0, 0, 100),     # RGBA color
    seed=None
)
```

### BlurEffects
Blur and motion effects.

```python
from utils import BlurEffects

# Gaussian blur
result = BlurEffects.gaussian_blur(img, radius=2.0)

# Motion blur
result = BlurEffects.motion_blur(
    img,
    angle=0,         # Angle in degrees
    distance=5       # Blur distance
)

# Light trail effect
result = BlurEffects.light_trail(
    img,
    intensity=50     # Effect intensity (0-100)
)
```

### PointillistEffect
Pointillist/stippling artistic effect.

```python
from utils import PointillistEffect

result = PointillistEffect.apply(
    img,
    dot_size=6,                    # Dot diameter
    spacing_ratio=1.2,             # Spacing between dots
    color_sample_mode='direct',    # 'direct' or 'average'
    bg_color='white',              # Background color
    jitter_strength=0.2            # Random position variation (0.0-1.0)
)
```

### TextureEffects
Texture and canvas simulation effects.

```python
from utils import TextureEffects

result = TextureEffects.canvas_texture(
    img,
    intensity=50     # Effect intensity (0-100)
)
```

### RetroDialog
Retro-style dialog box overlay.

```python
from utils import RetroDialog

result = RetroDialog.add_dialog(
    img,
    text="GAME OVER",
    pixel_size=4,
    dialog_color=(0, 0, 0),
    text_color=(255, 255, 255),
    border_color=(255, 255, 255)
)
```

### NoiseGenerator
Various noise generation utilities.

```python
from utils import NoiseGenerator

# Gaussian noise
result = NoiseGenerator.gaussian_noise(img, intensity=15)

# Controlled gaussian noise
result = NoiseGenerator.controlled_gaussian_noise(img, intensity=0.1)

# Fractal noise
noise_img = NoiseGenerator.fractal_noise(
    width=512,
    height=512,
    octaves=4,
    persistence=0.5,
    lacunarity=2.0
)
```

---

## Sprite Utils

### SpriteCutter
Utility for slicing sprite sheets into individual frames.

```python
from utils import SpriteCutter

# Parse dimensions
width, height = SpriteCutter.parse_dimensions("48x48")  # Returns (48, 48)
width, height = SpriteCutter.parse_dimensions("64")     # Returns (64, None)

# Detect transparent regions
regions = SpriteCutter.detect_transparent_regions(
    img,
    direction="h"    # 'h' for horizontal, 'v' for vertical
)

# Slice sprite sheet
frames = SpriteCutter.slice_sprite(
    img,
    width=48,           # Frame width
    height=48,          # Frame height
    slices=None,        # Number of slices (alternative to width)
    direction="h",      # 'h' or 'v'
    auto_detect=True,   # Auto-detect transparent regions
    padding=0,          # Padding around frames
    resize=None         # Tuple (width, height) to resize frames
)
```

---

## Parallel Utils

### ParallelProcessor
Parallel processing utilities for batch operations.

```python
from utils import ParallelProcessor

# Get optimal worker count
workers = ParallelProcessor.get_optimal_workers(io_bound=True)

# Process batch in parallel
results = ParallelProcessor.process_batch_parallel(
    file_paths,           # List of file paths
    process_func,         # Function to apply
    max_workers=None,     # Auto-detect optimal workers
    use_threading=False,  # Use threads (True) or processes (False)
    show_progress=True,   # Show progress bar
    description="Processing"
)

# Batch process images
results = ParallelProcessor.batch_process_images(
    input_dir="./input",
    output_dir="./output",
    effect_func=my_effect_function,   # Function(input_path, output_path)
    file_pattern="*",
    max_workers=None,
    create_output_dir=True
)
```

### MemoryOptimizer
Memory optimization utilities.

```python
from utils import MemoryOptimizer

# Calculate optimal preview size
preview_size = MemoryOptimizer.get_optimal_preview_size(
    original_size=(2000, 1500),
    max_dimension=800
)

# Create memory-efficient preview
preview_img = MemoryOptimizer.create_preview(
    img,
    max_dimension=800
)

# Process large image in chunks (experimental)
result = MemoryOptimizer.process_large_image_chunked(
    img,
    effect_func=my_effect,
    chunk_size=1024
)
```

### CacheManager
Simple LRU cache for effect previews.

```python
from utils import CacheManager

# Initialize cache
cache = CacheManager(max_size=50)

# Store value
cache.set("key", value)

# Retrieve value
value = cache.get("key")  # Returns None if not found

# Generate cache key from arguments
key = cache.generate_key("arg1", "arg2", param1="val1")

# Clear cache
cache.clear()
```

---

## Usage Examples

### Example 1: Apply Multiple Effects

```python
from utils import PixelArtEffect, ChromaticAberration, BlurEffects
from PIL import Image

# Load image
img = Image.open("input.jpg")

# Apply pixel art
img = PixelArtEffect.apply(img, colors=16, pixel_size=4)

# Add chromatic aberration
img = ChromaticAberration.apply(img, intensity=1.5)

# Add subtle blur
img = BlurEffects.gaussian_blur(img, radius=0.5)

# Save result
img.save("output.png")
```

### Example 2: Batch Process with Parallel

```python
from utils import ParallelProcessor, PixelArtEffect
from PIL import Image

def apply_retro_effect(input_path, output_path):
    img = Image.open(input_path)
    img = PixelArtEffect.apply(img, colors=16, pixel_size=4)
    img.save(output_path)
    return output_path

# Process all images in directory
ParallelProcessor.batch_process_images(
    input_dir="./photos",
    output_dir="./retro_photos",
    effect_func=apply_retro_effect,
    max_workers=8
)
```

### Example 3: Memory-Efficient Preview

```python
from utils import MemoryOptimizer, PixelArtEffect, CacheManager
from PIL import Image

# Initialize cache
cache = CacheManager(max_size=20)

def get_preview_with_cache(img_path, effect_params):
    # Generate cache key
    key = cache.generate_key(img_path, **effect_params)

    # Check cache
    cached = cache.get(key)
    if cached:
        return cached

    # Load and create preview
    img = Image.open(img_path)
    preview = MemoryOptimizer.create_preview(img, max_dimension=800)

    # Apply effect
    result = PixelArtEffect.apply(preview, **effect_params)

    # Cache result
    cache.set(key, result)

    return result

# Use cached preview
preview = get_preview_with_cache("large_image.jpg", {"colors": 16, "pixel_size": 4})
```

### Example 4: Cut Sprite Sheet

```python
from utils import SpriteCutter
from PIL import Image

# Load sprite sheet
sprite_sheet = Image.open("character_walk.png")

# Cut into frames (auto-detect)
frames = SpriteCutter.slice_sprite(
    sprite_sheet,
    width=48,
    height=48,
    auto_detect=True,
    padding=2
)

# Save individual frames
for i, frame in enumerate(frames):
    frame.save(f"frame_{i:03d}.png")
```

---

## Testing

Tests are located in `tests/` directory.

```bash
# Run all tests
python -m unittest discover tests

# Run specific test module
python -m unittest tests.test_effects_core

# Run specific test class
python -m unittest tests.test_effects_core.TestPixelArtEffect
```

---

## Performance Tips

1. **Use parallel processing** for batch operations
2. **Create previews** for real-time UI (max 800px dimension)
3. **Cache results** when applying same effects multiple times
4. **Use threading** for I/O-bound tasks (file operations)
5. **Use multiprocessing** for CPU-bound tasks (heavy effects)

---

## Notes

- All effect functions preserve image mode when possible (RGB, RGBA)
- Alpha channels are preserved in pixel art and chromatic aberration
- For video processing, use `PixelArtEffect.apply_to_frame()` with OpenCV frames
- Cache keys are case-sensitive and order-dependent for kwargs
