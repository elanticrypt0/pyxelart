# NoBG - Background Removal Script

A powerful Python script for removing backgrounds from images and GIFs using the rembg library with support for multiple output formats and quality control.

## Features

- Remove backgrounds from images and animated GIFs
- Multiple AI models for different use cases
- Alpha matting for improved edge quality
- Support for batch processing
- Multiple output formats (PNG, WebP, TIFF)
- Quality control for compression
- Preserves transparency in animations

## Requirements

```bash
pip install rembg pillow numpy tqdm opencv-python imageio
```

## Supported Models

- `u2net`: General purpose background removal
- `u2netp`: Lightweight version of u2net 
- `u2net_human_seg`: Optimized for human subjects (default)
- `silueta`: Alternative model option

## Usage

The script has four main modes:

### 1. Single Image Processing

```bash
python nobg.py image <input_image> [options]
```

### 2. Batch Image Processing

```bash
python nobg.py images <input_directory> [options]
```

### 3. Single GIF Processing

```bash
python nobg.py gif <input_gif> [options]
```

### 4. Batch GIF Processing

```bash
python nobg.py gifs <input_directory> [options]
```

## Command Line Arguments

### Common Options

```
--model MODEL               AI model to use (default: u2net_human_seg)
--alpha-matting            Enable alpha matting for better edges
--foreground-threshold N   Alpha matting foreground threshold (0-255, default: 240)
--background-threshold N   Alpha matting background threshold (0-255, default: 10)
--erode-size N            Alpha matting erode size (default: 10)
--quality N               Output quality (1-100, default: 95)
```

### Image-Specific Options

```
--format FORMAT           Output format: png, webp, tiff (default: png)
--output PATH            Custom output path
```

### Directory Processing Options

```
--output-dir DIR         Output directory (default: input_dir/nobg)
```

## Examples

### Basic Usage

```bash
# Remove background from a single image
python nobg.py image photo.jpg

# Process all images in a directory
python nobg.py images ./photos/
```

### Format and Quality Control

```bash
# Save as WebP with custom quality
python nobg.py image portrait.png --format webp --quality 85

# Process directory with WebP output
python nobg.py images ./input/ --format webp --quality 90
```

### Advanced Options

```bash
# Use alpha matting for better edges
python nobg.py image person.jpg --alpha-matting

# Custom model and thresholds
python nobg.py image face.png --model u2net --alpha-matting --foreground-threshold 250
```

### GIF Processing

```bash
# Remove background from animated GIF
python nobg.py gif animation.gif

# Batch process GIFs
python nobg.py gifs ./animations/ --quality 80
```

## Output Formats

### PNG (Default)
- Lossless compression
- Full transparency support
- Larger file sizes
- Best for maximum quality

### WebP
- Excellent compression
- Transparency support
- Smaller file sizes
- Good balance of quality and size

### TIFF
- Professional format
- Lossless compression
- Large file sizes
- Good for archival

## Quality Settings

- **1-50**: High compression, lower quality
- **51-85**: Balanced compression and quality
- **86-95**: Low compression, high quality (default: 95)
- **96-100**: Minimal compression, maximum quality

## Tips for Best Results

1. **Human Subjects**: Use `u2net_human_seg` model (default)
2. **Sharp Edges**: Enable `--alpha-matting`
3. **File Size**: Use WebP format with quality 80-90
4. **Complex Backgrounds**: Try different models
5. **Fine Details**: Adjust alpha matting thresholds

## Integration with Other Tools

This script works well in a pipeline with:

```bash
# 1. Remove background
python nobg.py image sprite.png --format webp

# 2. Apply retro effect
python pyxelart.py single sprite_nobg.webp --format webp

# 3. Extract frames if needed
python extract_frames.py sprite_nobg_retro.webp

# 4. Create Ren'Py definitions
python create_renpy_sprites.py frames/ character
```

## Performance Notes

- Alpha matting increases processing time but improves quality
- Batch processing is more efficient than individual files
- WebP offers the best size/quality ratio
- GIF processing can be memory intensive for large animations

## Troubleshooting

### Common Issues:

1. **Poor edge quality**
   - Enable `--alpha-matting`
   - Adjust threshold values
   - Try different models

2. **Large file sizes**
   - Use WebP format
   - Reduce quality setting
   - Consider PNG optimization

3. **Memory errors with GIFs**
   - Process smaller batches
   - Reduce GIF dimensions first
   - Close other applications

## License

MIT License - Feel free to use and modify as needed.

## Credits

This script uses the [rembg](https://github.com/danielgatis/rembg) library for background removal.