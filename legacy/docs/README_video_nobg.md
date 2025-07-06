# NoBG Video - Video Background Removal Script

A comprehensive Python script that extracts frames from video files and removes their backgrounds using the rembg library. Perfect for creating transparent video frames for animations, compositing, or game development.

## Features

- Extract frames from video files at custom frame rates
- Remove backgrounds from all extracted frames
- Support for multiple output formats (WebP, PNG, TIFF)
- Adjustable compression quality
- Alpha matting for improved edge quality
- Automatic snake_case output directory naming
- Option to keep original frames
- Progress tracking with tqdm

## Requirements

### Python Dependencies
```bash
pip install rembg pillow numpy tqdm opencv-python
```

### Script Dependencies
This script requires the following files in the same directory:
- `extract_frames.py` - For frame extraction functionality
- `nobg.py` - For background removal functionality

Make sure all three scripts are in the same directory.

## Quick Start

```bash
# Basic usage - extracts all frames and removes backgrounds
python nobg_video.py video.mp4

# Extract at 15 FPS with high quality
python nobg_video.py animation.mp4 --fps 15 --quality 90

# Use alpha matting for better edges
python nobg_video.py person.mov --alpha-matting
```

## Command Line Arguments

### Required Arguments

```
input                     Video file to process
```

### Optional Arguments

```
--output-dir DIR         Output directory (default: video_name_snake_case)
--fps FLOAT              Extract frames at specific FPS (default: all frames)
--model MODEL            AI model for background removal (default: u2net_human_seg)
--alpha-matting          Enable alpha matting for better edges
--foreground-threshold N Alpha matting foreground threshold (0-255, default: 240)
--background-threshold N Alpha matting background threshold (0-255, default: 10)
--erode-size N          Alpha matting erode size (default: 10)
--quality N             Output quality (1-100, default: 80)
--format FORMAT         Output format: webp, png, tiff (default: webp)
--keep-frames           Keep original extracted frames
```

## Supported Models

- `u2net`: General purpose background removal
- `u2netp`: Lightweight version of u2net
- `u2net_human_seg`: Optimized for human subjects (default)
- `silueta`: Alternative model option

## Supported Video Formats

- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- WebM (.webm)
- MKV (.mkv)

## Output Structure

The script creates a directory structure like this:

```
video_name/
├── frames_nobg/       # Frames with background removed
│   ├── frame_0000.webp
│   ├── frame_0001.webp
│   └── ...
└── frames_original/   # Original frames (if --keep-frames is used)
    ├── frame_0000.webp
    ├── frame_0001.webp
    └── ...
```

## Examples

### Basic Video Processing

```bash
# Process video with default settings
python nobg_video.py gameplay.mp4

# Output will be in 'gameplay/' directory
```

### Custom Frame Rate Extraction

```bash
# Extract at 10 FPS instead of original frame rate
python nobg_video.py animation.mp4 --fps 10

# Extract at 30 FPS for smoother animation
python nobg_video.py cutscene.mp4 --fps 30
```

### Quality and Format Control

```bash
# High quality PNG output
python nobg_video.py portrait.mov --format png --quality 95

# Compressed WebP for smaller file sizes
python nobg_video.py sprite.mp4 --format webp --quality 75
```

### Advanced Background Removal

```bash
# Use alpha matting for hair and fine details
python nobg_video.py person_talking.mp4 --alpha-matting

# Adjust alpha matting thresholds
python nobg_video.py character.mp4 --alpha-matting --foreground-threshold 250 --background-threshold 5
```

### Keeping Original Frames

```bash
# Keep both original and processed frames
python nobg_video.py reference.mp4 --keep-frames
```

### Custom Output Directory

```bash
# Specify custom output directory
python nobg_video.py input.mp4 --output-dir processed_frames
```

## Performance Tips

1. **Frame Rate**: Lower FPS values process faster and use less disk space
2. **Format**: WebP offers the best balance of quality and file size
3. **Quality**: 70-85 is usually sufficient for most use cases
4. **Alpha Matting**: Improves quality but increases processing time
5. **Model Selection**: 
   - Use `u2net_human_seg` for videos with people
   - Use `u2netp` for faster processing with acceptable quality
   - Use `u2net` for general purpose with best quality

## Integration with Other Tools

This script works well in a pipeline:

```bash
# 1. Process video to remove backgrounds
python nobg_video.py character_animation.mp4 --fps 24

# 2. Apply retro effect to frames
python pyxelart.py batch character_animation/frames_nobg/

# 3. Create sprite sheets or animations
python create_renpy_sprites.py character_animation/frames_nobg/ character
```

## Common Use Cases

1. **Game Development**: Extract character animations for 2D games
2. **Video Editing**: Create transparent overlays for compositing
3. **Animation**: Process rotoscoped animations
4. **VFX**: Extract subjects for visual effects work
5. **Content Creation**: Create stickers or GIFs from video clips

## Troubleshooting

### Memory Issues
- Process videos in smaller segments
- Reduce output quality
- Use lower FPS extraction
- Close other applications

### Poor Edge Quality
- Enable `--alpha-matting`
- Adjust threshold values
- Try different models
- Check if subject has good contrast with background

### Large Output Sizes
- Use WebP format
- Reduce quality setting (70-80 is usually sufficient)
- Extract fewer frames with `--fps` option

### Processing Speed
- Use `u2netp` model for faster processing
- Disable alpha matting if not needed
- Process on a machine with GPU support

## Notes

- The script automatically converts filenames to snake_case for output directories
- WebP format is recommended for best quality/size ratio
- Processing time depends on video length, resolution, and selected options
- GPU acceleration is used automatically if available through rembg

## License

MIT License - Feel free to use and modify as needed.

## Credits

This script uses:
- [rembg](https://github.com/danielgatis/rembg) for background removal
- [OpenCV](https://opencv.org/) for video processing
- [Pillow](https://python-pillow.org/) for image handling