# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyxelArt is a modernized suite of tools for creating retro-style images, videos, and sprites. The project has been **refactored to eliminate code duplication** and uses a **modular architecture** with shared utilities. The main entry point is `unified_cli.py` which combines multiple effects in a single tool.

## Environment Setup

### Dependencies Installation
Use UV (preferred) or pip to install dependencies:
```bash
# Using UV (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Or using pip
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Installation Scripts
- `install.sh` - Automated setup for Unix/Linux systems
- `install.ps1` - Windows PowerShell setup script

### External Dependencies
- **FFmpeg** - Required for video processing with audio preservation
- **System Requirements** - Python 3.11+

## Running the Application

The main entry point is `unified_cli.py` which provides a unified CLI:
```bash
# Basic pixel art effect
python unified_cli.py image.jpg --effects pixelart --colors 16

# Multiple effects combined
python unified_cli.py image.jpg --effects pixelart chromatic dialog --colors 8

# Specialized tools
python pyxelart_refactored.py single image.jpg --colors 16 --dialog --text "RETRO"
python chromatic_aberration_refactored.py single image.jpg --aberration-intensity 2.0
```

## Architecture Overview

### Core Components

1. **Main CLI Tools**
   - `unified_cli.py` - Primary tool for combining multiple effects
   - `pyxelart_refactored.py` - Specialized pixel art processor
   - `chromatic_aberration_refactored.py` - Chromatic aberration effects
   - `video_processor_refactored.py` - Video processing with effects

2. **Shared Utilities** (`utils/` directory)
   - `effects_core.py` - Core visual effects (pixel art, chromatic aberration, noise)
   - `format_utils.py` - Format handling and image saving
   - `file_utils.py` - File and directory processing
   - `cli_utils.py` - CLI argument parsing utilities
   - `aspect_ratio_utils.py` - Aspect ratio transformations
   - `ffmpeg_utils.py` - FFmpeg operations and checks

3. **Legacy Tools** (`legacy/` directory)
   - Original tools preserved for compatibility
   - `main.py` - Original interactive menu system
   - All original processing scripts

### Key Dependencies

- **PIL/Pillow** - Image manipulation and effects
- **OpenCV** - Video processing and computer vision
- **NumPy** - Numerical operations on image arrays
- **rembg** - AI-powered background removal
- **imageio** - GIF creation and video I/O
- **tqdm** - Progress bars for long-running operations

## Development Patterns

### Command-Line Interface Pattern
All tools follow a consistent argparse-based CLI pattern:
- Single/batch processing modes
- Configurable output paths and formats
- Progress tracking with tqdm
- Error handling with cleanup

### File Processing Conventions
- Support for multiple input formats (PNG, JPEG, WebP, MP4, etc.)
- Batch processing capabilities for directories
- Automatic output directory creation
- Quality and compression control

### Common Parameters
- `--colors` - Number of colors for retro effects (default: 16)
- `--pixel-size` - Pixelation level (default: 4)
- `--format` - Output format (png/jpg/webp/mp4/gif)
- `--quality` - Output quality (1-100)
- `--aspect-ratio` - Aspect ratio adjustment (4:3/1:1/original)

## Common Development Tasks

### Testing Individual Tools
Each tool can be run independently:
```bash
python unified_cli.py input.png --effects pixelart --colors 16 --pixel-size 4
python pyxelart_refactored.py single input.png --colors 16 --pixel-size 4
python chromatic_aberration_refactored.py single input.png --aberration-intensity 1.5
python video_processor_refactored.py single video.mp4 --colors 16 --fps 30
```

### Running Combined Effects
Use the unified CLI for multiple effects:
```bash
python unified_cli.py input.png --effects pixelart chromatic dialog --colors 16 --aberration-intensity 1.5 --dialog-text "RETRO"
```

### Adding New Effects
When adding new image effects:
1. Add the effect to `utils/effects_core.py` as a new class
2. Integrate it into `unified_cli.py` in the effects processing loop
3. Optionally create a specialized tool following the pattern of existing refactored tools
4. Use the shared utilities from `utils/` for CLI, file processing, and format handling

## Testing and Quality Assurance

### Testing Setup
The project includes test files in the `test/` directory with sample images and videos for manual testing.

### Quality Control
- Use `--quality` parameter for output file size control
- Test with various input formats and sizes
- Verify audio preservation in video processing
- Test batch processing with multiple files

## File Organization

- **Root level** - Refactored tools (`unified_cli.py`, `*_refactored.py`)
- **utils/** - Shared utility modules
- **legacy/** - Original tools (preserved for compatibility)
- **test/** - Sample files and test outputs
- **videostest/** - Video processing test outputs
- Project configuration: `pyproject.toml`, `requirements.txt`

## Common Issues and Solutions

1. **FFmpeg not found** - Install FFmpeg for full video support
2. **Memory issues** - Process smaller batches or reduce quality
3. **Import errors** - Ensure all dependencies are installed
4. **Permission errors** - Check file permissions and output directory access

## Integration Notes

The refactored architecture provides:
- **Unified CLI** for most common use cases combining multiple effects
- **Specialized tools** for specific workflows requiring fine-tuned control
- **Shared utilities** eliminating code duplication and ensuring consistency
- **Legacy compatibility** with all original tools preserved in `legacy/` directory
- **Modular design** making it easy to extend with new effects or formats

Use `unified_cli.py` as the primary entry point, falling back to specialized tools when needed.