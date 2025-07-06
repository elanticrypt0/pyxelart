#!/usr/bin/env python3
"""
CLI utilities for PyxelArt
Centralized argument parsing and CLI helpers
"""

import argparse
from typing import List, Dict, Any, Optional
from pathlib import Path


class CLIArgumentFactory:
    """Factory for creating common CLI arguments"""
    
    @staticmethod
    def add_input_arguments(parser: argparse.ArgumentParser, mode_choices: List[str] = None):
        """Add common input arguments"""
        if mode_choices is None:
            mode_choices = ['single', 'batch']
        
        parser.add_argument('mode', choices=mode_choices, 
                          help='Processing mode')
        parser.add_argument('input', 
                          help='Input file or directory path')
    
    @staticmethod
    def add_output_arguments(parser: argparse.ArgumentParser, required: bool = False):
        """Add common output arguments"""
        parser.add_argument('--output', '-o', 
                          help='Output file path (for single mode)', 
                          required=required)
        parser.add_argument('--output-dir', '-od', 
                          help='Output directory (for batch mode)')
    
    @staticmethod
    def add_quality_arguments(parser: argparse.ArgumentParser):
        """Add quality-related arguments"""
        parser.add_argument('--quality', '-q', type=int, default=95, 
                          help='Output quality (1-100, default: 95)')
        parser.add_argument('--format', '-f', 
                          choices=['png', 'jpg', 'jpeg', 'webp', 'tiff', 'bmp'],
                          help='Output format')
        parser.add_argument('--optimize-web', action='store_true',
                          help='Optimize for web use')
    
    @staticmethod
    def add_pixel_art_arguments(parser: argparse.ArgumentParser):
        """Add pixel art effect arguments"""
        parser.add_argument('--colors', '-c', type=int, default=16,
                          help='Number of colors for pixel art effect (default: 16)')
        parser.add_argument('--pixel-size', '-p', type=int, default=4,
                          help='Pixel size for pixelation (default: 4)')
        parser.add_argument('--no-noise', action='store_true',
                          help='Disable noise addition')
        parser.add_argument('--noise-intensity', type=int, default=15,
                          help='Noise intensity (default: 15)')
    
    @staticmethod
    def add_aspect_ratio_arguments(parser: argparse.ArgumentParser):
        """Add aspect ratio arguments"""
        parser.add_argument('--aspect-ratio', '-ar',
                          choices=['original', '4:3', '1:1'],
                          default='original',
                          help='Target aspect ratio (default: original)')
        parser.add_argument('--aspect-method', 
                          choices=['resize', 'crop'],
                          default='resize',
                          help='Method for aspect ratio adjustment (default: resize)')
    
    @staticmethod
    def add_dialog_arguments(parser: argparse.ArgumentParser):
        """Add dialog box arguments"""
        parser.add_argument('--dialog', action='store_true',
                          help='Add retro dialog box')
        parser.add_argument('--text', '-t', default='RETRO STYLE',
                          help='Dialog text (default: "RETRO STYLE")')
        parser.add_argument('--dialog-color', default='black',
                          help='Dialog background color (default: black)')
        parser.add_argument('--text-color', default='white',
                          help='Text color (default: white)')
    
    @staticmethod
    def add_chromatic_aberration_arguments(parser: argparse.ArgumentParser):
        """Add chromatic aberration arguments"""
        parser.add_argument('--aberration-intensity', type=float, default=1.0,
                          help='Chromatic aberration intensity (default: 1.0)')
        parser.add_argument('--red-shift', nargs=2, type=int, default=[2, 0],
                          help='Red channel shift (x y, default: 2 0)')
        parser.add_argument('--green-shift', nargs=2, type=int, default=[0, 0],
                          help='Green channel shift (x y, default: 0 0)')
        parser.add_argument('--blue-shift', nargs=2, type=int, default=[-2, 0],
                          help='Blue channel shift (x y, default: -2 0)')
        parser.add_argument('--lens-effect', action='store_true',
                          help='Apply lens distortion effect')
        parser.add_argument('--edge-mode', 
                          choices=['transparent', 'black', 'white', 'clamp'],
                          default='transparent',
                          help='Edge handling mode (default: transparent)')
    
    @staticmethod
    def add_video_arguments(parser: argparse.ArgumentParser):
        """Add video processing arguments"""
        parser.add_argument('--fps', type=float,
                          help='Target FPS for processing')
        parser.add_argument('--video-quality', type=int, default=23,
                          help='Video quality (CRF: 0-51, lower is better, default: 23)')
        parser.add_argument('--preset', 
                          choices=['ultrafast', 'superfast', 'veryfast', 'faster', 
                                 'fast', 'medium', 'slow', 'slower', 'veryslow'],
                          default='medium',
                          help='Encoding preset (default: medium)')
        parser.add_argument('--video-format', 
                          choices=['mp4', 'avi', 'mov', 'mkv', 'webm'],
                          default='mp4',
                          help='Video output format (default: mp4)')
    
    @staticmethod
    def add_gif_arguments(parser: argparse.ArgumentParser):
        """Add GIF processing arguments"""
        parser.add_argument('--frame-skip', type=int, default=2,
                          help='Frame skip for GIF (default: 2)')
        parser.add_argument('--gif-fps', type=int, default=10,
                          help='GIF framerate (default: 10)')
        parser.add_argument('--gif-optimize', action='store_true',
                          help='Optimize GIF size')
    
    @staticmethod
    def add_audio_arguments(parser: argparse.ArgumentParser):
        """Add audio processing arguments"""
        parser.add_argument('--audio-format', 
                          choices=['mp3', 'wav', 'aac', 'flac', 'ogg'],
                          default='mp3',
                          help='Audio output format (default: mp3)')
        parser.add_argument('--audio-quality', default='192k',
                          help='Audio bitrate/quality (default: 192k)')
        parser.add_argument('--sample-rate', type=int,
                          help='Audio sample rate')
        parser.add_argument('--channels', type=int, choices=[1, 2],
                          help='Audio channels (1=mono, 2=stereo)')
    
    @staticmethod
    def add_background_removal_arguments(parser: argparse.ArgumentParser):
        """Add background removal arguments"""
        parser.add_argument('--model', '-m',
                          choices=['u2net', 'u2netp', 'u2net_human_seg', 'silueta'],
                          default='u2net_human_seg',
                          help='Background removal model (default: u2net_human_seg)')
        parser.add_argument('--alpha-matting', action='store_true',
                          help='Use alpha matting for better edges')
    
    @staticmethod
    def add_common_arguments(parser: argparse.ArgumentParser):
        """Add commonly used arguments"""
        parser.add_argument('--verbose', '-v', action='store_true',
                          help='Verbose output')
        parser.add_argument('--overwrite', action='store_true',
                          help='Overwrite existing files')
        parser.add_argument('--recursive', '-r', action='store_true',
                          help='Process directories recursively')
        parser.add_argument('--parallel', '-j', type=int, default=1,
                          help='Number of parallel workers (default: 1)')


class CLIValidator:
    """CLI input validation utilities"""
    
    @staticmethod
    def validate_file_path(path: str, must_exist: bool = True) -> Path:
        """Validate file path"""
        file_path = Path(path)
        
        if must_exist and not file_path.exists():
            raise argparse.ArgumentTypeError(f"File not found: {path}")
        
        if must_exist and file_path.is_dir():
            raise argparse.ArgumentTypeError(f"Expected file, got directory: {path}")
        
        return file_path
    
    @staticmethod
    def validate_directory_path(path: str, must_exist: bool = True) -> Path:
        """Validate directory path"""
        dir_path = Path(path)
        
        if must_exist and not dir_path.exists():
            raise argparse.ArgumentTypeError(f"Directory not found: {path}")
        
        if must_exist and not dir_path.is_dir():
            raise argparse.ArgumentTypeError(f"Expected directory, got file: {path}")
        
        return dir_path
    
    @staticmethod
    def validate_quality(value: str) -> int:
        """Validate quality value (1-100)"""
        try:
            quality = int(value)
            if not 1 <= quality <= 100:
                raise argparse.ArgumentTypeError("Quality must be between 1 and 100")
            return quality
        except ValueError:
            raise argparse.ArgumentTypeError("Quality must be an integer")
    
    @staticmethod
    def validate_positive_int(value: str) -> int:
        """Validate positive integer"""
        try:
            num = int(value)
            if num <= 0:
                raise argparse.ArgumentTypeError("Value must be positive")
            return num
        except ValueError:
            raise argparse.ArgumentTypeError("Value must be an integer")
    
    @staticmethod
    def validate_positive_float(value: str) -> float:
        """Validate positive float"""
        try:
            num = float(value)
            if num <= 0:
                raise argparse.ArgumentTypeError("Value must be positive")
            return num
        except ValueError:
            raise argparse.ArgumentTypeError("Value must be a number")
    
    @staticmethod
    def validate_color(value: str) -> str:
        """Validate color value (basic validation)"""
        # Support color names and hex values
        if value.lower() in ['black', 'white', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta']:
            return value.lower()
        
        if value.startswith('#') and len(value) in [4, 7]:
            try:
                int(value[1:], 16)
                return value
            except ValueError:
                pass
        
        # Try RGB tuple format
        if value.startswith('(') and value.endswith(')'):
            try:
                rgb_str = value[1:-1]
                rgb_values = [int(x.strip()) for x in rgb_str.split(',')]
                if len(rgb_values) == 3 and all(0 <= v <= 255 for v in rgb_values):
                    return value
            except ValueError:
                pass
        
        raise argparse.ArgumentTypeError(f"Invalid color format: {value}")


class CLIBuilder:
    """Builder class for creating CLI parsers"""
    
    def __init__(self, description: str, prog_name: str = None):
        self.parser = argparse.ArgumentParser(description=description, prog=prog_name)
        self.factory = CLIArgumentFactory()
        self.validator = CLIValidator()
    
    def add_input_args(self, mode_choices: List[str] = None):
        """Add input arguments"""
        self.factory.add_input_arguments(self.parser, mode_choices)
        return self
    
    def add_output_args(self, required: bool = False):
        """Add output arguments"""
        self.factory.add_output_arguments(self.parser, required)
        return self
    
    def add_quality_args(self):
        """Add quality arguments"""
        self.factory.add_quality_arguments(self.parser)
        return self
    
    def add_pixel_art_args(self):
        """Add pixel art arguments"""
        self.factory.add_pixel_art_arguments(self.parser)
        return self
    
    def add_aspect_ratio_args(self):
        """Add aspect ratio arguments"""
        self.factory.add_aspect_ratio_arguments(self.parser)
        return self
    
    def add_dialog_args(self):
        """Add dialog arguments"""
        self.factory.add_dialog_arguments(self.parser)
        return self
    
    def add_chromatic_aberration_args(self):
        """Add chromatic aberration arguments"""
        self.factory.add_chromatic_aberration_arguments(self.parser)
        return self
    
    def add_video_args(self):
        """Add video arguments"""
        self.factory.add_video_arguments(self.parser)
        return self
    
    def add_gif_args(self):
        """Add GIF arguments"""
        self.factory.add_gif_arguments(self.parser)
        return self
    
    def add_audio_args(self):
        """Add audio arguments"""
        self.factory.add_audio_arguments(self.parser)
        return self
    
    def add_background_removal_args(self):
        """Add background removal arguments"""
        self.factory.add_background_removal_arguments(self.parser)
        return self
    
    def add_common_args(self):
        """Add common arguments"""
        self.factory.add_common_arguments(self.parser)
        return self
    
    def add_custom_arg(self, *args, **kwargs):
        """Add custom argument"""
        self.parser.add_argument(*args, **kwargs)
        return self
    
    def build(self) -> argparse.ArgumentParser:
        """Build and return the parser"""
        return self.parser


class CLIHelper:
    """CLI helper utilities"""
    
    @staticmethod
    def print_processing_info(args: argparse.Namespace, tool_name: str):
        """Print processing information"""
        print(f"\n=== {tool_name} ===")
        print(f"Mode: {args.mode}")
        print(f"Input: {args.input}")
        
        if hasattr(args, 'output') and args.output:
            print(f"Output: {args.output}")
        if hasattr(args, 'output_dir') and args.output_dir:
            print(f"Output directory: {args.output_dir}")
        
        print()
    
    @staticmethod
    def confirm_overwrite(file_path: str) -> bool:
        """Confirm file overwrite"""
        if Path(file_path).exists():
            response = input(f"File {file_path} exists. Overwrite? [y/N]: ")
            return response.lower() in ['y', 'yes']
        return True
    
    @staticmethod
    def get_processing_params(args: argparse.Namespace) -> Dict[str, Any]:
        """Extract processing parameters from args"""
        params = {}
        
        # Quality parameters
        if hasattr(args, 'quality'):
            params['quality'] = args.quality
        if hasattr(args, 'format'):
            params['format'] = args.format
        
        # Pixel art parameters
        if hasattr(args, 'colors'):
            params['colors'] = args.colors
        if hasattr(args, 'pixel_size'):
            params['pixel_size'] = args.pixel_size
        if hasattr(args, 'no_noise'):
            params['add_noise'] = not args.no_noise
        if hasattr(args, 'noise_intensity'):
            params['noise_intensity'] = args.noise_intensity
        
        # Aspect ratio parameters
        if hasattr(args, 'aspect_ratio'):
            params['aspect_ratio'] = args.aspect_ratio
        if hasattr(args, 'aspect_method'):
            params['aspect_method'] = args.aspect_method
        
        # Dialog parameters
        if hasattr(args, 'dialog'):
            params['add_dialog'] = args.dialog
        if hasattr(args, 'text'):
            params['dialog_text'] = args.text
        
        # Video parameters
        if hasattr(args, 'fps'):
            params['fps'] = args.fps
        if hasattr(args, 'video_quality'):
            params['video_quality'] = args.video_quality
        if hasattr(args, 'preset'):
            params['preset'] = args.preset
        
        return params


# Convenience functions for common CLI patterns
def create_image_processor_cli(description: str) -> argparse.ArgumentParser:
    """Create CLI for image processing tools"""
    return (CLIBuilder(description)
            .add_input_args()
            .add_output_args()
            .add_quality_args()
            .add_pixel_art_args()
            .add_aspect_ratio_args()
            .add_dialog_args()
            .add_common_args()
            .build())

def create_video_processor_cli(description: str) -> argparse.ArgumentParser:
    """Create CLI for video processing tools"""
    return (CLIBuilder(description)
            .add_input_args()
            .add_output_args()
            .add_quality_args()
            .add_pixel_art_args()
            .add_aspect_ratio_args()
            .add_video_args()
            .add_common_args()
            .build())

def create_background_removal_cli(description: str) -> argparse.ArgumentParser:
    """Create CLI for background removal tools"""
    return (CLIBuilder(description)
            .add_input_args()
            .add_output_args()
            .add_quality_args()
            .add_background_removal_args()
            .add_common_args()
            .build())

def create_effect_cli(description: str, effect_name: str) -> argparse.ArgumentParser:
    """Create CLI for specific effect tools"""
    builder = (CLIBuilder(description)
               .add_input_args()
               .add_output_args()
               .add_quality_args()
               .add_common_args())
    
    # Add effect-specific arguments
    if 'chromatic' in effect_name.lower():
        builder.add_chromatic_aberration_args()
    elif 'pixel' in effect_name.lower():
        builder.add_pixel_art_args()
    
    return builder.build()