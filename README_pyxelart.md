# PyxelArt - Retro Image Effect Script

A Python script that applies retro pixelated effects to images, supporting multiple formats and preserving transparency when possible.

## Features

- Apply pixelation and reduced color palettes for retro aesthetics
- Support for multiple image formats (PNG, JPEG, WebP)
- Preserve transparency in PNG and WebP formats
- Adjustable aspect ratios (4:3, 1:1, or custom)
- Optional retro-style dialog boxes
- Batch processing for multiple images
- Quality control for compression
- Noise/dithering effects for authentic retro look

## Requirements

```bash
pip install pillow numpy tqdm
```

## Usage

The script has two main modes:

### 1. Single Image Processing

```bash
python pyxelart.py single <input_image> [options]
```

### 2. Batch Image Processing

```bash
python pyxelart.py batch <input_directory> [options]
```

## Command Line Arguments

### Common Options

```
--width WIDTH              Output width in pixels
--height HEIGHT           Output height in pixels
--colors N               Number of colors in palette (default: 16)
--pixel-size N           Size of pixelation effect (default: 4)
--dialog                 Add retro-style dialog box
--text TEXT              Text for dialog box
--aspect-ratio RATIO     Aspect ratio: 4:3, 1:1, or original (default: original)
--aspect-method METHOD   Method for aspect ratio: resize or crop (default: resize)
--quality N              Output quality 1-100 (default: 95)
--format FORMAT          Output format: png, jpg, webp (default: preserve original)
```

### Single Mode Specific

```
--output PATH            Custom output path (default: input_retro-cN-pN.ext)
```

### Batch Mode Specific

```
--output-dir DIR         Output directory (default: input_dir/retro)
```

## Examples

### Basic Usage

```bash
# Apply retro effect to a single image
python pyxelart.py single sprite.png

# Process all images in a directory
python pyxelart.py batch ./sprites/
```

### Customize Effects

```bash
# 8 colors with heavy pixelation
python pyxelart.py single character.png --colors 8 --pixel-size 8

# 32 colors with light pixelation
python pyxelart.py single landscape.jpg --colors 32 --pixel-size 2
```

### Format and Quality Control

```bash
# Convert to WebP with lower quality for smaller size
python pyxelart.py single photo.jpg --format webp --quality 80

# Convert to PNG with maximum quality
python pyxelart.py single sprite.png --format png --quality 100
```

### Aspect Ratio Adjustments

```bash
# Convert to 4:3 aspect ratio by resizing
python pyxelart.py single widescreen.png --aspect-ratio 4:3 --aspect-method resize

# Convert to square by cropping
python pyxelart.py single portrait.jpg --aspect-ratio 1:1 --aspect-method crop
```

### Adding Dialog Boxes

```bash
# Add retro dialog box with custom text
python pyxelart.py single character.png --dialog --text "Hello, adventurer!"

# Batch process with dialog boxes
python pyxelart.py batch ./npcs/ --dialog --text "Welcome to our village!"
```

### Complete Examples

```bash
# Full retro game sprite treatment
python pyxelart.py single hero.png --colors 16 --pixel-size 4 --aspect-ratio 1:1 --format png

# Process cutscene images with dialog
python pyxelart.py batch ./cutscenes/ --colors 32 --dialog --text "Chapter 1" --format webp --quality 85

# Convert modern photos to retro style
python pyxelart.py batch ./photos/ --colors 16 --pixel-size 6 --aspect-ratio 4:3 --format jpg --quality 90
```

## Output Format Details

### PNG
- Lossless compression
- Full transparency support
- Best for sprites and pixel art
- Larger file sizes

### JPEG
- Lossy compression
- No transparency support
- Good for photos and backgrounds
- Smaller file sizes

### WebP
- Modern format with excellent compression
- Supports transparency
- Best balance of quality and size
- Ideal for web use

## Tips for Best Results

1. **Color Depth**:
   - 8-16 colors: Classic retro look
   - 32-64 colors: More detail while maintaining retro feel
   - 128+ colors: Subtle retro effect

2. **Pixel Size**:
   - 2-3: Subtle pixelation
   - 4-6: Balanced retro effect
   - 8+: Heavy pixelation for extreme retro look

3. **Aspect Ratios**:
   - 4:3: Classic gaming/TV ratio
   - 1:1: Perfect for icons and avatars
   - Original: Preserve source proportions

4. **Format Selection**:
   - PNG for sprites and transparency
   - WebP for web delivery
   - JPEG for backgrounds without transparency

## Integration with Other Tools

Works well in a pipeline with:

```bash
# 1. Remove background
python nobg.py image sprite.png

# 2. Apply retro effect
python pyxelart.py single sprite_nobg.png --colors 16

# 3. Extract frames
python extract_frames.py sprite_nobg_retro.png

# 4. Create sprite sheets
python create_renpy_sprites.py frames/ character
```

## Performance Notes

- Processing time increases with image size
- Batch processing is more efficient than individual files
- WebP offers the best compression/quality ratio
- PNG optimization can be slow for large images

## Troubleshooting

### Common Issues:

1. **Transparency Lost**
   - Ensure using PNG or WebP format
   - Check if source image has alpha channel

2. **Color Banding**
   - Increase color depth
   - Reduce pixel size
   - Try different noise levels

3. **Large File Sizes**
   - Use WebP format
   - Reduce quality setting
   - Decrease output dimensions

## License

MIT License - Feel free to use and modify as needed.