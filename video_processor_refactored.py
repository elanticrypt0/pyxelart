#!/usr/bin/env python3
"""
Refactored Video Processor
Demonstrates usage of the new utils modules for video processing
"""

import sys
import os
import cv2
import tempfile
from pathlib import Path

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from effects_core import PixelArtEffect
from format_utils import VideoFormatManager, AudioFormatManager
from file_utils import VideoProcessor, DirectoryManager
from cli_utils import create_video_processor_cli, CLIHelper
from aspect_ratio_utils import AspectRatioManager
from ffmpeg_utils import FFmpegManager


class VideoEffectProcessor:
    """Video processor using shared utilities"""
    
    def __init__(self):
        self.video_processor = VideoProcessor()
        self.ffmpeg = FFmpegManager()
    
    def process_single_video(self, input_path: str, output_path: str, **params) -> bool:
        """
        Process a single video with effects
        
        Args:
            input_path: Input video path
            output_path: Output video path
            **params: Processing parameters
        
        Returns:
            bool: True if successful
        """
        try:
            # Check FFmpeg availability
            if not self.ffmpeg.is_available():
                print("Error: FFmpeg is required for video processing")
                return False
            
            # Get video info
            video_info = self.ffmpeg.get_video_info(input_path)
            if not video_info:
                print(f"Error: Could not read video info from {input_path}")
                return False
            
            print(f"Processing video: {video_info['width']}x{video_info['height']} @ {video_info.get('fps', 'unknown')} FPS")
            
            # Create temporary directory for frames
            with tempfile.TemporaryDirectory(prefix="pyxelart_video_") as temp_dir:
                temp_path = Path(temp_dir)
                
                # Step 1: Extract frames
                print("Extracting frames...")
                frames_dir = temp_path / "frames"
                frames_dir.mkdir(exist_ok=True)
                
                success = self.ffmpeg.extract_frames(
                    input_path,
                    str(frames_dir),
                    fps=params.get('fps'),
                    format='png',
                    quality=95
                )
                
                if not success:
                    print("Error: Failed to extract frames")
                    return False
                
                # Step 2: Process frames
                print("Processing frames with effects...")
                processed_frames_dir = temp_path / "processed"
                processed_frames_dir.mkdir(exist_ok=True)
                
                frame_files = sorted(frames_dir.glob("*.png"))
                
                for i, frame_file in enumerate(frame_files):
                    if i % 100 == 0:
                        print(f"Processing frame {i+1}/{len(frame_files)}")
                    
                    # Load frame
                    frame = cv2.imread(str(frame_file))
                    if frame is None:
                        continue
                    
                    # Apply aspect ratio if specified
                    if params.get('aspect_ratio', 'original') != 'original':
                        target_ratio = AspectRatioManager.parse_aspect_ratio(params['aspect_ratio'])
                        frame = AspectRatioManager.apply_to_frame(
                            frame, target_ratio, params.get('aspect_method', 'resize')
                        )
                    
                    # Apply pixel art effect
                    processed_frame = PixelArtEffect.apply_to_frame(
                        frame,
                        colors=params.get('colors', 16),
                        pixel_size=params.get('pixel_size', 4),
                        add_noise=params.get('add_noise', True),
                        noise_intensity=params.get('noise_intensity', 15)
                    )
                    
                    # Save processed frame
                    output_frame_path = processed_frames_dir / frame_file.name
                    cv2.imwrite(str(output_frame_path), processed_frame)
                
                # Step 3: Reconstruct video
                print("Reconstructing video...")
                
                # Get codec and quality parameters
                format_name = params.get('video_format', 'mp4')
                codec = VideoFormatManager.get_ffmpeg_codec(format_name)
                quality_params = VideoFormatManager.get_ffmpeg_quality_params(
                    params.get('video_quality', 23),
                    params.get('preset', 'medium')
                )
                
                # Calculate FPS
                fps = params.get('fps', video_info.get('fps', 30))
                
                success = self.ffmpeg.create_video_from_frames(
                    str(processed_frames_dir),
                    output_path,
                    fps=fps,
                    codec=codec,
                    quality=int(quality_params['crf']),
                    preset=quality_params['preset']
                )
                
                if not success:
                    print("Error: Failed to create output video")
                    return False
                
                # Step 4: Add audio back if present
                audio_info = self.ffmpeg.get_audio_info(input_path)
                if audio_info and audio_info.get('codec'):
                    print("Adding audio track...")
                    
                    # Extract audio to temporary file
                    audio_temp = temp_path / "audio.aac"
                    
                    audio_success = self.ffmpeg.extract_audio(
                        input_path,
                        str(audio_temp),
                        format='aac',
                        bitrate='128k'
                    )
                    
                    if audio_success:
                        # Combine video and audio
                        final_output = temp_path / "final_output.mp4"
                        
                        combine_success = self.ffmpeg.convert_video(
                            output_path,
                            str(final_output),
                            codec=codec,
                            quality=int(quality_params['crf']),
                            preset=quality_params['preset']
                        )
                        
                        if combine_success:
                            # Replace output with final version
                            import shutil
                            shutil.move(str(final_output), output_path)
                        else:
                            print("Warning: Failed to add audio, video saved without audio")
                    else:
                        print("Warning: Failed to extract audio, video saved without audio")
                
                print("✓ Video processing completed successfully!")
                return True
                
        except Exception as e:
            print(f"Error processing video {input_path}: {e}")
            return False
    
    def process_batch(self, input_dir: str, output_dir: str = None, **params) -> list:
        """
        Process a batch of videos
        
        Args:
            input_dir: Input directory
            output_dir: Output directory (optional)
            **params: Processing parameters
        
        Returns:
            list: Results for each file
        """
        return self.video_processor.process_directory(
            input_dir=input_dir,
            output_dir=output_dir,
            process_func=self.process_single_video,
            overwrite=params.get('overwrite', False),
            recursive=params.get('recursive', False),
            **params
        )


def main():
    """Main function with CLI"""
    # Create CLI parser
    parser = create_video_processor_cli("Apply effects to videos")
    args = parser.parse_args()
    
    # Print processing info
    CLIHelper.print_processing_info(args, "Video Effect Processor (Refactored)")
    
    # Check FFmpeg
    is_available, message = FFmpegManager.check_installation()
    print(f"FFmpeg status: {message}")
    if not is_available:
        print("Error: FFmpeg is required for video processing")
        return 1
    
    # Extract processing parameters
    params = CLIHelper.get_processing_params(args)
    
    # Create processor
    processor = VideoEffectProcessor()
    
    # Process based on mode
    if args.mode == 'single':
        # Validate input file
        if not Path(args.input).exists():
            print(f"Error: Input file not found: {args.input}")
            return 1
        
        # Generate output path if not provided
        if not args.output:
            from format_utils import FormatManager
            output_path = FormatManager.generate_output_path(
                args.input,
                suffix='_processed',
                format_name=args.video_format
            )
        else:
            output_path = args.output
        
        # Check overwrite
        if Path(output_path).exists() and not args.overwrite:
            if not CLIHelper.confirm_overwrite(output_path):
                print("Operation cancelled.")
                return 1
        
        # Process single file
        success = processor.process_single_video(args.input, output_path, **params)
        
        if success:
            print(f"✓ Successfully processed: {output_path}")
            return 0
        else:
            print("✗ Processing failed")
            return 1
    
    elif args.mode == 'batch':
        # Validate input directory
        if not Path(args.input).exists():
            print(f"Error: Input directory not found: {args.input}")
            return 1
        
        # Process batch
        results = processor.process_batch(args.input, args.output_dir, **params)
        
        # Report results
        successful = sum(results)
        total = len(results)
        
        print(f"\nBatch processing completed:")
        print(f"✓ Successful: {successful}/{total}")
        print(f"✗ Failed: {total - successful}/{total}")
        
        return 0 if successful > 0 else 1
    
    else:
        print(f"Unknown mode: {args.mode}")
        return 1


if __name__ == "__main__":
    sys.exit(main())