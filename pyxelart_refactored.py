#!/usr/bin/env python3
"""
Refactored Pixel Art Processor
Demonstrates usage of the new utils modules
"""

import sys
import os
from pathlib import Path

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from effects_core import PixelArtEffect, RetroDialog
from format_utils import FormatManager
from file_utils import ImageProcessor
from cli_utils import create_image_processor_cli, CLIHelper
from aspect_ratio_utils import apply_aspect_ratio
from PIL import Image


class PixelArtProcessor:
    """Refactored pixel art processor using shared utilities"""
    
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.format_manager = FormatManager()
    
    def process_single_image(self, input_path: str, output_path: str, **params) -> bool:
        """
        Process a single image with pixel art effect
        
        Args:
            input_path: Input image path
            output_path: Output image path
            **params: Processing parameters
        
        Returns:
            bool: True if successful
        """
        try:
            # Load image
            with Image.open(input_path) as img:
                # Apply aspect ratio if specified
                if params.get('aspect_ratio', 'original') != 'original':
                    img = apply_aspect_ratio(
                        img, 
                        params.get('aspect_ratio', 'original'),
                        params.get('aspect_method', 'resize')
                    )
                
                # Apply pixel art effect
                processed_img = PixelArtEffect.apply(
                    img,
                    colors=params.get('colors', 16),
                    pixel_size=params.get('pixel_size', 4),
                    add_noise=params.get('add_noise', True),
                    noise_intensity=params.get('noise_intensity', 15)
                )
                
                # Add dialog if requested
                if params.get('add_dialog', False):
                    processed_img = RetroDialog.add_dialog(
                        processed_img,
                        text=params.get('dialog_text', 'RETRO STYLE'),
                        pixel_size=params.get('pixel_size', 4)
                    )
                
                # Save with appropriate format settings
                success = self.format_manager.save_image(
                    processed_img,
                    output_path,
                    format_name=params.get('format'),
                    quality=params.get('quality', 95),
                    optimize_for_web=params.get('optimize_web', False)
                )
                
                return success
                
        except Exception as e:
            print(f"Error processing {input_path}: {e}")
            return False
    
    def process_batch(self, input_dir: str, output_dir: str = None, **params) -> list:
        """
        Process a batch of images
        
        Args:
            input_dir: Input directory
            output_dir: Output directory (optional)
            **params: Processing parameters
        
        Returns:
            list: Results for each file
        """
        return self.image_processor.process_directory(
            input_dir=input_dir,
            output_dir=output_dir,
            process_func=self.process_single_image,
            overwrite=params.get('overwrite', False),
            recursive=params.get('recursive', False),
            **params
        )


def main():
    """Main function with CLI"""
    # Create CLI parser using the utility
    parser = create_image_processor_cli("Apply pixel art effect to images")
    args = parser.parse_args()
    
    # Print processing info
    CLIHelper.print_processing_info(args, "Pixel Art Processor (Refactored)")
    
    # Extract processing parameters
    params = CLIHelper.get_processing_params(args)
    
    # Create processor
    processor = PixelArtProcessor()
    
    # Process based on mode
    if args.mode == 'single':
        # Validate input file
        if not Path(args.input).exists():
            print(f"Error: Input file not found: {args.input}")
            return 1
        
        # Generate output path if not provided
        if not args.output:
            output_path = FormatManager.generate_output_path(
                args.input,
                suffix='_pixel_art',
                format_name=args.format
            )
        else:
            output_path = args.output
        
        # Check overwrite
        if Path(output_path).exists() and not args.overwrite:
            if not CLIHelper.confirm_overwrite(output_path):
                print("Operation cancelled.")
                return 1
        
        # Process single file
        success = processor.process_single_image(args.input, output_path, **params)
        
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