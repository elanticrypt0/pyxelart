# PyxelArt Video - Retro Video Effect Script

A Python script that applies retro pixelated effects to video files while preserving audio, creating nostalgic video content with authentic retro aesthetics.

## Features

- Apply pixelation and color reduction to videos
- Preserve original audio track (requires FFmpeg)
- Support for multiple video formats
- Adjustable aspect ratios (4:3, 1:1, or custom)
- Optional retro-style dialog boxes
- Batch processing for multiple videos
- Compression quality control
- Frame rate control

## Requirements

### Python Dependencies
```bash
pip install pillow numpy opencv-python tqdm
```

### System Requirements
- **FFmpeg** (optional but recommended for audio preservation)
  - Windows: Download from https://ffmpeg.org/download.html
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg`

## Usage

The script has two main modes:

### 1. Single Video Processing

```bash
python pyxelart_video.py single <input_video> [options]
```

### 2. Batch Video Processing

```bash
python pyxelart_video.py batch <input_directory> [options]
```

## Command Line Arguments

### Common Options

```
--width WIDTH              Output width in pixels
--height HEIGHT            Output height in pixels
--colors N                 Number of colors in palette (default: 16)
--pixel-size N             Size of pixelation effect (default: 4)
--frame-skip N             Process every Nth frame (default: 1)
--fps N                    Output video frame rate (default: original)
--dialog                   Add retro-style dialog box
--text TEXT                Text for dialog box
--format FORMAT            Output format: .mp4, .avi, .mov, .mkv (default: .mp4)
--aspect-ratio RATIO       Aspect ratio: 4:3, 1:1, or original (default: original)
--aspect-method METHOD     Method for aspect ratio: resize or crop (default: resize)
--quality N                Compression quality 1-51 (default: 23, lower is better)
--preset PRESET            Encoding preset (default: medium)
```

### Single Mode Specific

```
--output PATH              Custom output path (default: input_retro-cN-pN.mp4)
```

### Batch Mode Specific

```
--output-dir DIR           Output directory (default: input_dir/retro)
```

## Supported Video Formats

### Input Formats
- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- WebM (.webm)
- FLV (.flv)
- WMV (.wmv)

### Output Formats
- MP4 (.mp4) - Recommended
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)

## Examples

### Basic Usage

```bash
# Apply retro effect to a video
python pyxelart_video.py single gameplay.mp4

# Process all videos in a directory
python pyxelart_video.py batch ./videos/
```

### Customize Effects

```bash
# Heavy pixelation with limited colors
python pyxelart_video.py single movie.mp4 --colors 8 --pixel-size 8

# Subtle retro effect
python pyxelart_video.py single interview.mp4 --colors 64 --pixel-size 2
```

### Quality and Compression

```bash
# High quality output
python pyxelart_video.py single important.mp4 --quality 18 --preset slow

# Smaller file size
python pyxelart_video.py single large_video.mp4 --quality 28 --preset faster

# Maximum compression
python pyxelart_video.py single huge_video.mp4 --quality 32 --preset ultrafast
```

### Aspect Ratio Control

```bash
# Convert to 4:3 for CRT TV effect
python pyxelart_video.py single modern.mp4 --aspect-ratio 4:3

# Create square video for social media
python pyxelart_video.py single content.mp4 --aspect-ratio 1:1 --aspect-method crop
```

### Adding Dialog Boxes

```bash
# Add retro dialog overlay
python pyxelart_video.py single cutscene.mp4 --dialog --text "Game Over"

# Batch process with custom text
python pyxelart_video.py batch ./story/ --dialog --text "Chapter 1"
```

### Complete Examples

```bash
# Full retro gaming treatment
python pyxelart_video.py single gameplay.mp4 --colors 16 --pixel-size 6 --aspect-ratio 4:3 --quality 20

# Create VHS-style effect
python pyxelart_video.py single home_video.mp4 --colors 32 --pixel-size 4 --quality 26 --preset fast

# Process game cutscenes
python pyxelart_video.py batch ./cutscenes/ --colors 24 --dialog --text "Loading..." --format .mkv
```

## Encoding Presets

Presets affect encoding speed and file size:

- `ultrafast`: Fastest encoding, largest files
- `superfast`: Very fast, large files
- `veryfast`: Fast encoding
- `faster`: Faster than default
- `fast`: Slightly faster than default
- `medium`: Default balance
- `slow`: Better compression
- `slower`: Much better compression
- `veryslow`: Best compression, slowest

## Quality Settings

Quality (CRF) values:
- `0`: Lossless (huge files)
- `15-18`: Visually lossless
- `19-23`: High quality (default: 23)
- `24-28`: Good quality, smaller files
- `29-35`: Acceptable quality, much smaller
- `36-51`: Low quality, minimum size

## Tips for Best Results

1. **For YouTube/Streaming**:
   ```bash
   python pyxelart_video.py single video.mp4 --quality 20 --preset slow --colors 32
   ```

2. **For Social Media**:
   ```bash
   python pyxelart_video.py single content.mp4 --aspect-ratio 1:1 --quality 24 --preset medium
   ```

3. **For Archival**:
   ```bash
   python pyxelart_video.py single important.mp4 --quality 16 --preset veryslow --format .mkv
   ```

4. **For Quick Preview**:
   ```bash
   python pyxelart_video.py single test.mp4 --quality 28 --preset ultrafast --pixel-size 8
   ```

## Audio Handling

- **With FFmpeg**: Audio is preserved from the original video
- **Without FFmpeg**: Output video will have no audio
- Audio codec: AAC at 128kbps (when FFmpeg is available)

## Performance Notes

- Processing time increases with:
  - Video length
  - Resolution
  - Slower presets
  - Lower quality values
- Memory usage scales with resolution
- FFmpeg is required for audio preservation

## Integration with Other Tools

```bash
# 1. Remove background from video
python nobg_video.py character.mp4

# 2. Apply retro effect
python pyxelart_video.py single character/frames_nobg/ --colors 16

# 3. Extract frames for further processing
python extract_frames.py character_retro.mp4

# 4. Create sprite sheets
python create_renpy_sprites.py frames/ character
```

## Troubleshooting

### Common Issues:

1. **No Audio in Output**
   - Install FFmpeg
   - Check FFmpeg is in system PATH
   - Verify with `ffmpeg -version`

2. **Large File Sizes**
   - Increase quality value (higher = more compression)
   - Use faster preset
   - Reduce resolution
   - Decrease color depth

3. **Slow Processing**
   - Use faster preset
   - Reduce resolution
   - Skip frames with `--frame-skip`

4. **Quality Issues**
   - Lower quality value (lower = better quality)
   - Use slower preset
   - Increase color depth
   - Reduce pixel size

## Output Naming Convention

Output files are named: `inputname_retro-c{colors}-p{pixelsize}.{format}`

Example: `video_retro-c16-p4.mp4`

## License

MIT License - Feel free to use and modify as needed.