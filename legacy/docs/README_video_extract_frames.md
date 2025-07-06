# Extract Frames - Video/GIF Frame Extraction Script

A Python script that extracts frames from video files and animated GIFs, with support for transparency preservation and multiple output formats.

## Features

- Extract frames from videos and animated GIFs
- Preserve transparency in GIF extraction
- Support for multiple video formats
- Frame rate control for videos
- Output in PNG or WebP format
- Quality control for WebP compression
- Progress tracking with tqdm

## Requirements

```bash
pip install opencv-python pillow numpy tqdm
```

## Usage

```bash
python extract_frames.py <input_file> [options]
```

## Command Line Arguments

```
input                     Video or GIF file to process
--output-dir, -o         Output directory (default: input_filename_frames)
--fps FLOAT              Extract at specific FPS (video only)
--no-alpha               Do not preserve transparency
--format FORMAT          Output format: png or webp (default: webp)
--quality N              WebP compression quality 1-100 (default: 80)
```

## Supported Input Formats

### Video Formats
- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- WebM (.webm)
- MKV (.mkv)

### Animation Format
- GIF (.gif)

## Examples

### Basic Usage

```bash
# Extract frames from a video
python extract_frames.py video.mp4

# Extract frames from a GIF
python extract_frames.py animation.gif
```

### Frame Rate Control (Video Only)

```bash
# Extract at 10 FPS
python extract_frames.py gameplay.mp4 --fps 10

# Extract at 30 FPS for smooth animation
python extract_frames.py cutscene.mp4 --fps 30

# Extract all frames (original FPS)
python extract_frames.py video.mp4
```

### Output Format Options

```bash
# Extract as PNG (lossless, larger files)
python extract_frames.py sprite.gif --format png

# Extract as WebP with custom quality
python extract_frames.py video.mp4 --format webp --quality 90
```

### Output Directory Control

```bash
# Specify custom output directory
python extract_frames.py animation.gif --output-dir ./extracted_frames/

# Short form
python extract_frames.py video.mp4 -o ./frames/
```

### Transparency Handling

```bash
# Preserve transparency (default)
python extract_frames.py character.gif

# Disable transparency preservation
python extract_frames.py sprite.gif --no-alpha
```

### Complete Examples

```bash
# Extract high-quality PNG frames from GIF
python extract_frames.py animated_logo.gif --format png

# Extract compressed frames from video at 15 FPS
python extract_frames.py gameplay.mp4 --fps 15 --format webp --quality 75

# Extract all frames without transparency
python extract_frames.py animation.gif --no-alpha --format png
```

## Output Details

### File Naming
Frames are saved as: `frame_XXXX.{format}`
- XXXX: Zero-padded frame number (0000, 0001, etc.)

### WebP Quality Settings
- 1-50: High compression, lower quality
- 51-75: Balanced compression
- 76-90: Low compression, high quality (default: 80)
- 91-100: Minimal compression, maximum quality

### PNG vs WebP
- **PNG**: Lossless, larger files, full quality
- **WebP**: Lossy/lossless options, smaller files, configurable quality

## GIF Extraction Features

The script handles complex GIF animations:
- Preserves transparency
- Handles frame disposal methods
- Reconstructs full frames from optimized GIFs
- Maintains proper f