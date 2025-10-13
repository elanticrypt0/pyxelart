# PyxelArt GIF - Video to Retro GIF Converter

A Python script that converts video files to animated GIFs with retro pixelated effects, perfect for creating nostalgic animations and game assets.

## Features

- Convert videos to retro-styled animated GIFs
- Apply pixelation and color reduction effects
- Frame rate control and frame skipping
- Adjustable aspect ratios (4:3, 1:1, or custom)
- Optional retro-style dialog boxes
- Batch processing for multiple videos
- Progress tracking with tqdm

## Requirements

```bash
pip install pillow numpy opencv-python imageio tqdm
```

## Usage

The script has two main modes:

### 1. Single Video Processing

```bash
python pyxelart_gif.py single <input_video> [options]
```

### 2. Batch Video Processing

```bash
python pyxelart_gif.py batch <input_directory> [options]
```

## Command Line Arguments

### Common Options

```
--width WIDTH              Output width in pixels
--height HEIGHT            Output height in pixels
--colors N                 Number of colors in palette (default: 16)
--pixel-size N             Size of pixelation effect (default: 4)
--frame-skip N             Process every Nth frame (default: 2)
--fps N                    Output GIF frame rate (default: 10)
--dialog                   Add retro-style dialog box
--text TEXT                Text for dialog box
--aspect-ratio RATIO       Aspect ratio: 4:3, 1:1, or original (default: original)
--aspect-method METHOD     Method for aspect ratio: resize or crop (default: resize)
```

### Single Mode Specific

```
--output PATH              Custom output path (default: input_retro-cN-pN.gif)
```

### Batch Mode Specific

```
--output-dir DIR           Output directory (default: input_dir/retro)
```

## Supported Video Formats

- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- WebM (.webm)
- FLV (.flv)
- WMV (.wmv)

## Examples

### Basic Usage

```bash
# Convert a video to retro GIF
python pyxelart_gif.py single gameplay.mp4

# Process all videos in a directory
python pyxelart_gif.py batch ./videos/
```

### Customize Effects

```bash
# Heavy pixelation with 8 colors
python pyxelart_gif.py single animation.mp4 --colors 8 --pixel-size 8

# Subtle retro effect with more colors
python pyxelart_gif.py single cutscene.mp4 --colors 32 --pixel-size 2
```

### Frame Rate Control

```bash
# Extract every frame at 30 FPS
python pyxelart_gif.py single fast_action.mp4 --frame-skip 1 --fps 30

# Skip frames for smaller file size
python pyxelart_gif.py single long_video.mp4 --frame-skip 4 --fps 8
```

### Aspect Ratio Adjustments

```bash
# Convert to 4:3 for retro TV look
python pyxelart_gif.py single widescreen.mp4 --aspect-ratio 4:3

# Create square GIFs for social media
python pyxelart_gif.py single video.mp4 --aspect-ratio 1:1 --aspect-method crop
```

### Adding Dialog Boxes

```bash
# Add retro dialog with custom text
python pyxelart_gif.py single character.mp4 --dialog --text "Level Complete!"

# Batch process with dialog
python pyxelart_gif.py batch ./cutscenes/ --dialog --text "Game Over"
```

### Complete Examples

```bash
# Create retro game animation
python pyxelart_gif.py single sprite_anim.mp4 --colors 16 --pixel-size 4 --fps 12 --aspect-ratio 1:1

# Convert gameplay footage to retro style
python pyxelart_gif.py single gameplay.mp4 --colors 32 --pixel-size 6 --frame-skip 3 --fps 10

# Process cutscenes with dialog
python pyxelart_gif.py batch ./story/ --colors 24 --dialog --text "Chapter 1" --aspect-ratio 4:3
```

## Performance Optimization

### Frame Skip Settings
- `1`: Process every frame (maximum quality, largest file)
- `2`: Process every other frame (default, good balance)
- `3-4`: Good for long videos or slow motion
- `5+`: Maximum compression, may look choppy

### FPS Settings
- `5-8`: Very retro, choppy animation
- `10-12`: Classic animation feel (default: 10)
- `15-20`: Smooth animation
- `24+`: Near-video quality

### Color Depth
- `4-8`: Extreme retro, very small files
- `16`: Classic retro look (default)
- `32-64`: More detail, larger files
- `128+`: Subtle effect, near-original quality

## Tips for Best Results

1. **For Game Sprites**:
   ```bash
   python pyxelart_gif.py single sprite.mp4 --colors 16 --pixel-size 4 --fps 12
   ```

2. **For Cutscenes**:
   ```bash
   python pyxelart_gif.py single cutscene.mp4 --colors 32 --frame-skip 2 --aspect-ratio 4:3
   ```

3. **For Social Media**:
   ```bash
   python pyxelart_gif.py single video.mp4 --aspect-ratio 1:1 --fps 15 --colors 64
   ```

4. **For Maximum Compression**:
   ```bash
   python pyxelart_gif.py single long_video.mp4 --frame-skip 4 --fps 8 --colors 8
   ```

## Integration with Other Tools

Works in a pipeline with:

```bash
# 1. Remove background from video
python nobg_video.py character.mp4

# 2. Convert to retro GIF
python pyxelart_gif.py single character/frames_nobg/ --colors 16

# 3. Extract frames from GIF
python extract_frames.py character_retro.gif

# 4. Create sprite sheets
python create_renpy_sprites.py frames/ character
```

## Output Naming Convention

Output files are named: `inputname_retro-c{colors}-p{pixelsize}.gif`

Example: `video_retro-c16-p4.gif`

## Troubleshooting

### Common Issues:

1. **Large File Sizes**
   - Increase frame-skip value
   - Reduce FPS
   - Lower color count
   - Decrease output dimensions

2. **Choppy Animation**
   - Decrease frame-skip value
   - Increase FPS
   - Check source video frame rate

3. **Poor Quality**
   - Increase color depth
   - Reduce pixel size
   - Try different aspect ratio method

4. **Memory Errors**
   - Process shorter segments
   - Increase frame-skip
   - Reduce output dimensions

## Notes

- GIF format has color limitations (256 colors max)
- Large videos can consume significant memory
- Processing time increases with video length and resolution
- Audio is not preserved in GIF format

## License

MIT License - Feel free to use and modify as needed.