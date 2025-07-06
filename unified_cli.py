#!/usr/bin/env python3
"""
Unified CLI for PyxelArt
Simplified interface using the new modular architecture
"""

import sys
import os
from pathlib import Path
import argparse

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from effects_core import PixelArtEffect, ChromaticAberration, RetroDialog, NoiseGenerator
from format_utils import FormatManager
from file_utils import ImageProcessor, VideoProcessor
from aspect_ratio_utils import apply_aspect_ratio
from ffmpeg_utils import FFmpegManager
from PIL import Image
import cv2
import tempfile


class UnifiedProcessor:
    """Unified processor for all effects and formats"""
    
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.video_processor = VideoProcessor()
        self.format_manager = FormatManager()
        self.ffmpeg = FFmpegManager()
    
    def process_image(self, input_path: str, output_path: str, effects: list, **params) -> bool:
        """Process image with specified effects"""
        try:
            with Image.open(input_path) as img:
                # Apply aspect ratio if specified
                if params.get('aspect_ratio', 'original') != 'original':
                    img = apply_aspect_ratio(
                        img, 
                        params.get('aspect_ratio', 'original'),
                        params.get('aspect_method', 'resize')
                    )
                
                # Apply effects in order
                for effect in effects:
                    if effect == 'pixelart':
                        img = PixelArtEffect.apply(
                            img,
                            colors=params.get('colors', 16),
                            pixel_size=params.get('pixel_size', 4),
                            add_noise=params.get('add_noise', True),
                            noise_intensity=params.get('noise_intensity', 15)
                        )
                    
                    elif effect == 'chromatic':
                        img = ChromaticAberration.apply(
                            img,
                            intensity=params.get('aberration_intensity', 1.0),
                            red_shift=params.get('red_shift', (2, 0)),
                            green_shift=params.get('green_shift', (0, 0)),
                            blue_shift=params.get('blue_shift', (-2, 0)),
                            lens_effect=params.get('lens_effect', False),
                            edge_mode=params.get('edge_mode', 'transparent')
                        )
                    
                    elif effect == 'noise':
                        img = NoiseGenerator.gaussian_noise(
                            img,
                            intensity=params.get('noise_intensity', 15)
                        )
                    
                    elif effect == 'dialog':
                        img = RetroDialog.add_dialog(
                            img,
                            text=params.get('dialog_text', 'RETRO STYLE'),
                            pixel_size=params.get('pixel_size', 4)
                        )
                
                # Save with appropriate format settings
                return self.format_manager.save_image(
                    img,
                    output_path,
                    format_name=params.get('format'),
                    quality=params.get('quality', 95),
                    optimize_for_web=params.get('optimize_web', False)
                )
                
        except Exception as e:
            print(f"Error processing {input_path}: {e}")
            return False
    
    def process_video(self, input_path: str, output_path: str, effects: list, **params) -> bool:
        """Process video with specified effects"""
        try:
            if not self.ffmpeg.is_available():
                print("Error: FFmpeg is required for video processing")
                return False
            
            # Get video info
            video_info = self.ffmpeg.get_video_info(input_path)
            if not video_info:
                print(f"Error: Could not read video info from {input_path}")
                return False
            
            print(f"Processing video: {video_info['width']}x{video_info['height']} @ {video_info.get('fps', 'unknown')} FPS")
            
            # Create temporary directory
            with tempfile.TemporaryDirectory(prefix="pyxelart_unified_") as temp_dir:
                temp_path = Path(temp_dir)
                
                # Extract frames
                print("Extracting frames...")
                frames_dir = temp_path / "frames"
                frames_dir.mkdir(exist_ok=True)
                
                success = self.ffmpeg.extract_frames(
                    input_path,
                    str(frames_dir),
                    fps=params.get('fps'),
                    format='png'
                )
                
                if not success:
                    print("Error: Failed to extract frames")
                    return False
                
                # Process frames
                print("Processing frames...")
                processed_frames_dir = temp_path / "processed"
                processed_frames_dir.mkdir(exist_ok=True)
                
                frame_files = sorted(frames_dir.glob("*.png"))
                
                for i, frame_file in enumerate(frame_files):
                    if i % 50 == 0:
                        print(f"Processing frame {i+1}/{len(frame_files)}")
                    
                    # Convert frame to PIL Image for processing
                    frame = cv2.imread(str(frame_file))
                    if frame is None:
                        continue
                    
                    # Convert to RGB for PIL
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(frame_rgb)
                    
                    # Process with same logic as images
                    temp_output = temp_path / f"temp_frame_{i}.png"
                    success = self.process_image(
                        str(frame_file), 
                        str(temp_output), 
                        effects, 
                        **params
                    )
                    
                    if success:
                        # Convert back to OpenCV format
                        processed_pil = Image.open(temp_output)
                        processed_array = cv2.cvtColor(
                            cv2.imread(str(temp_output)), 
                            cv2.COLOR_BGR2RGB
                        )
                        
                        # Save as processed frame
                        output_frame_path = processed_frames_dir / frame_file.name
                        cv2.imwrite(str(output_frame_path), 
                                  cv2.cvtColor(processed_array, cv2.COLOR_RGB2BGR))
                
                # Reconstruct video
                print("Reconstructing video...")
                fps = params.get('fps', video_info.get('fps', 30))
                
                success = self.ffmpeg.create_video_from_frames(
                    str(processed_frames_dir),
                    output_path,
                    fps=fps,
                    quality=params.get('video_quality', 23),
                    preset=params.get('preset', 'medium')
                )
                
                if success:
                    print("✓ Video processing completed!")
                    return True
                else:
                    print("Error: Failed to create output video")
                    return False
                
        except Exception as e:
            print(f"Error processing video {input_path}: {e}")
            return False


def create_unified_cli():
    """Create unified CLI parser"""
    parser = argparse.ArgumentParser(
        description="Unified PyxelArt processor - apply multiple effects to images and videos"
    )
    
    # Input/Output
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('--output', '-o', help='Output file (for single file processing)')
    parser.add_argument('--output-dir', '-od', help='Output directory (for batch processing)')
    
    # Processing mode
    parser.add_argument('--mode', choices=['single', 'batch'], default='single',
                       help='Processing mode (default: single)')
    parser.add_argument('--type', choices=['auto', 'image', 'video'], default='auto',
                       help='Force input type (default: auto-detect)')
    
    # Effects to apply (can specify multiple)
    parser.add_argument('--effects', '-e', nargs='+', 
                       choices=['pixelart', 'chromatic', 'noise', 'dialog'],
                       default=['pixelart'],
                       help='Effects to apply (default: pixelart)')
    
    # Pixel art parameters
    parser.add_argument('--colors', '-c', type=int, default=16,
                       help='Number of colors (default: 16)')
    parser.add_argument('--pixel-size', '-p', type=int, default=4,
                       help='Pixel size (default: 4)')
    parser.add_argument('--no-noise', action='store_true',
                       help='Disable noise addition')
    parser.add_argument('--noise-intensity', type=int, default=15,
                       help='Noise intensity (default: 15)')
    
    # Chromatic aberration parameters
    parser.add_argument('--aberration-intensity', type=float, default=1.0,
                       help='Chromatic aberration intensity (default: 1.0)')
    parser.add_argument('--lens-effect', action='store_true',
                       help='Apply lens distortion')
    
    # Dialog parameters
    parser.add_argument('--dialog-text', default='RETRO STYLE',
                       help='Dialog text (default: "RETRO STYLE")')
    
    # Aspect ratio
    parser.add_argument('--aspect-ratio', choices=['original', '4:3', '1:1', '16:9'],
                       default='original', help='Aspect ratio (default: original)')
    parser.add_argument('--aspect-method', choices=['resize', 'crop'], default='resize',
                       help='Aspect ratio method (default: resize)')
    
    # Quality and format
    parser.add_argument('--quality', '-q', type=int, default=95,
                       help='Output quality (default: 95)')
    parser.add_argument('--format', choices=['png', 'jpg', 'webp', 'mp4', 'avi'],
                       help='Output format (auto-detect if not specified)')
    
    # Video parameters
    parser.add_argument('--fps', type=float, help='Target FPS for video processing')
    parser.add_argument('--video-quality', type=int, default=23,
                       help='Video quality CRF (default: 23)')
    parser.add_argument('--preset', default='medium',
                       help='Video encoding preset (default: medium)')
    
    # Common options
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files')
    parser.add_argument('--recursive', '-r', action='store_true', help='Process recursively')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    return parser


def main():
    """Main function"""
    parser = create_unified_cli()
    args = parser.parse_args()
    
    print("=== PyxelArt Unified Processor ===")
    print(f"Input: {args.input}")
    print(f"Effects: {', '.join(args.effects)}")
    print()
    
    # Check FFmpeg if processing videos
    if args.type == 'video' or (args.type == 'auto' and 
                               Path(args.input).suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']):
        is_available, message = FFmpegManager.check_installation()
        print(f"FFmpeg status: {message}")
        if not is_available:
            print("Warning: FFmpeg not available, video processing will be limited")
    
    # Prepare parameters
    params = {
        'colors': args.colors,
        'pixel_size': args.pixel_size,
        'add_noise': not args.no_noise,
        'noise_intensity': args.noise_intensity,
        'aberration_intensity': args.aberration_intensity,
        'lens_effect': args.lens_effect,
        'dialog_text': args.dialog_text,
        'aspect_ratio': args.aspect_ratio,
        'aspect_method': args.aspect_method,
        'quality': args.quality,
        'format': args.format,
        'fps': args.fps,
        'video_quality': args.video_quality,
        'preset': args.preset,
        'overwrite': args.overwrite,
        'recursive': args.recursive,
        'red_shift': (2, 0),
        'green_shift': (0, 0),
        'blue_shift': (-2, 0),
        'edge_mode': 'transparent'
    }
    
    # Create processor
    processor = UnifiedProcessor()
    
    # Determine input type
    input_path = Path(args.input)
    
    if args.mode == 'single':
        if not input_path.exists():
            print(f"Error: Input file not found: {args.input}")
            return 1
        
        # Determine file type
        is_video = False
        if args.type == 'video':
            is_video = True
        elif args.type == 'auto':
            is_video = input_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        
        # Generate output path
        if not args.output:
            suffix = '_' + '_'.join(args.effects)
            output_path = FormatManager.generate_output_path(
                str(input_path),
                suffix=suffix,
                format_name=args.format
            )
        else:
            output_path = args.output
        
        # Process file
        if is_video:
            success = processor.process_video(str(input_path), output_path, args.effects, **params)
        else:
            success = processor.process_image(str(input_path), output_path, args.effects, **params)
        
        if success:
            print(f"✓ Successfully processed: {output_path}")
            return 0
        else:
            print("✗ Processing failed")
            return 1
    
    elif args.mode == 'batch':
        print("Batch processing not yet implemented in unified CLI")
        print("Please use individual tools for batch processing")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())