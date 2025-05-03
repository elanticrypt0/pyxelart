# Retro Media Processing Tools Suite

A unified command-line interface (CLI) for a comprehensive suite of tools that apply retro effects, remove backgrounds, and process images and videos.

## Features

- 🎨 **Interactive Menu System**: Easy-to-use interface for all tools
- 🖼️ **Image Processing**: Apply retro effects and remove backgrounds from images
- 🎬 **Video Processing**: Convert videos to retro style or animated GIFs
- 🎞️ **Frame Extraction**: Extract frames from videos and GIFs
- 🔄 **Complete Pipeline**: Combine background removal with retro effects
- 🎯 **Batch Processing**: Process multiple files at once
- 🌈 **Color-coded Output**: Enhanced readability with ANSI colors

## Quick Start

### Using UV (Fastest method)
```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository and navigate to it
cd retro-media-tools

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip sync requirements.txt

# Run the main script
python main.py
```

### Using traditional pip
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the main script
python main.py
```

This launches the interactive menu where you can select from various operations.

## Available Operations

1. **Apply retro effect to image(s)**
   - Single image or batch processing
   - Customizable colors, pixelation, and aspect ratios
   - Support for PNG, JPEG, and WebP formats

2. **Convert video to retro GIF**
   - Create animated GIFs with retro aesthetics
   - Frame rate control and frame skipping
   - Aspect ratio adjustments

3. **Apply retro effect to video**
   - Preserve audio while applying retro effects
   - Multiple output formats (MP4, AVI, MOV, MKV)
   - Quality and compression control

4. **Extract frames from video/GIF**
   - Extract at specific frame rates
   - Preserve transparency
   - Output as PNG or WebP

5. **Remove background from image(s)**
   - Multiple AI models for different subjects
   - Alpha matting for better edges
   - Batch processing support

6. **Remove background from video frames**
   - Process entire videos frame by frame
   - Choose output format and quality
   - Option to keep original frames

7. **Extract audio from video**
   - Multiple audio formats (MP3, WAV, AAC, FLAC, OGG)
   - Customizable quality and bitrate
   - Batch processing support

8. **Complete pipeline (images/video)**
   - Combine background removal with retro effects
   - Works for both images and videos
   - Streamlined workflow for best results

9. **Video processing pipeline**
   - Extract audio + frames + remove backgrounds
   - Optional retro effects
   - Organized project structure

10. **Show help for a specific tool**
    - Access detailed help for each script
    - View all available options and parameters

## Requirements

### Python Dependencies
The project requires the following main libraries:
- Pillow (image processing)
- NumPy (numerical operations)
- OpenCV (video processing)
- tqdm (progress bars)
- rembg (background removal)
- imageio (GIF/video handling)

### System Requirements
- Python 3.7+
- FFmpeg (optional, for audio preservation in videos)

## Installation

### Method 1: Using UV (Recommended)

UV is a fast Python package installer and resolver. If you don't have UV installed:

```bash
# Install UV (on macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

Then install the project dependencies:

```bash
# Create a virtual environment with UV
uv venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies using UV
uv pip install -r requirements.txt

# Or install specific packages
uv pip install pillow numpy opencv-python tqdm rembg imageio
```

### Method 2: Using pip

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Method 3: Using UV with project sync

If you want to use UV's project management features:

```bash
# Initialize a new project (if needed)
uv init

# Add dependencies to pyproject.toml
uv add pillow numpy opencv-python tqdm rembg imageio

# Sync the project
uv sync
```

### Files needed

Make sure all script files are in the same directory:
- `main.py`
- `pyxelart.py`
- `pyxelart_gif.py`
- `pyxelart_video.py`
- `extract_frames.py`
- `nobg.py`
- `nobg_video

## Usage Examples

### Interactive Mode

Simply run:
```bash
python main.py
```

The interactive menu will guide you through each operation with prompts for all necessary parameters.

### Example Workflow

1. **Remove background from a video**:
   - Select option 6
   - Enter video path
   - Choose output settings

2. **Apply retro effect to processed frames**:
   - Select option 1
   - Choose batch mode
   - Point to the frames directory
   - Set retro parameters

3. **Or use the complete pipeline (option 7)**:
   - Automatically handles both steps
   - Simplified workflow

## Menu Navigation

- Use number keys (1-11) to select operations
- Follow the prompts for each parameter
- Default values are shown in brackets [default]
- Press Enter to accept default values
- Use Ctrl+C to cancel current operation

## Color Coding

The interface uses colors for better readability:
- 🔵 Blue: Menu options
- 🟢 Green: Success messages
- 🔴 Red: Error messages
- 🟡 Yellow: Warnings
- 🔷 Cyan: Commands being executed
- 🟣 Purple: Section headers

## Tips

1. **First-time users**: Start with option 8 to explore help for each tool
2. **Batch processing**: Use batch modes for processing multiple files efficiently
3. **Quality settings**: Lower quality values mean better quality (for video compression)
4. **Aspect ratios**: Use 4:3 for classic retro look, 1:1 for social media
5. **Background removal**: Use `u2net_human_seg` model for people, `u2net` for general objects

## Common Workflows

### Create Retro Game Sprites
```
1. Remove background from character images (option 5)
2. Apply retro effect with 16 colors and pixel size 4 (option 1)
3. Extract frames if needed (option 4)
```

### Process Video for Social Media
```
1. Convert video to retro GIF (option 2)
2. Set aspect ratio to 1:1
3. Use moderate compression for smaller file size
```

### Full Video Processing
```
1. Use complete pipeline (option 8)
2. Choose video input
3. Set retro parameters
4. Get processed frames with transparent background
```

### Game Development Workflow
```
1. Use video processing pipeline (option 9)
2. Extract audio in WAV format for game engine
3. Extract frames at desired FPS
4. Remove backgrounds from all frames
5. Optional: Apply retro effects
6. Import assets into your game engine
```

## Troubleshooting

### Common Issues:

1. **Script not found errors**
   - Ensure all scripts are in the same directory as main.py
   - Check file permissions

2. **Import errors**
   - Install all required dependencies
   - Use correct Python version (3.7+)

3. **FFmpeg warnings**
   - Install FFmpeg for full video support
   - Videos will process without audio if FFmpeg is missing

4. **Memory errors**
   - Process smaller batches
   - Reduce output quality/resolution
   - Close other applications

## Advanced Usage

The main.py script constructs command-line arguments for each tool. You can:
- View the generated commands before execution
- Copy commands for direct use
- Modify the script for custom workflows

## License

MIT License - Feel free to use and modify as needed.

## Credits

Retro Media Processing Tools Suite - A unified interface for media processing scripts.