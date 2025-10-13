#!/usr/bin/env python3
"""
sprite_cutter.py - Una herramienta para recortar sprites de animación para videojuegos

Esta herramienta permite recortar una imagen (o un directorio de imágenes) en múltiples frames,
ya sea por un número específico de divisiones o según un ancho y alto determinados.
Puede detectar automáticamente las zonas transparentes para optimizar el recorte.
"""

import os
import sys
import argparse
from pathlib import Path
import re
from PIL import Image
import numpy as np

def parse_dimensions(dimension_str):
    """Parse a dimension string like '48' or '48x48' into width and height."""
    if "x" in dimension_str:
        width, height = map(int, dimension_str.lower().split("x"))
        return width, height
    else:
        return int(dimension_str), None

def detect_transparent_regions(img, direction="h"):
    """Detect non-transparent regions of the image."""
    if img.mode != 'RGBA':
        # Convert to RGBA if not already
        img = img.convert('RGBA')
    
    # Convert to numpy array for faster processing
    data = np.array(img)
    alpha = data[:, :, 3]
    
    if direction == "h":
        # For horizontal direction, find vertical lines with non-transparent pixels
        non_transparent_cols = []
        for x in range(img.width):
            if np.any(alpha[:, x] > 0):
                non_transparent_cols.append(x)
    else:
        # For vertical direction, find horizontal lines with non-transparent pixels
        non_transparent_cols = []
        for y in range(img.height):
            if np.any(alpha[y, :] > 0):
                non_transparent_cols.append(y)
    
    # Group consecutive columns to find regions
    regions = []
    if non_transparent_cols:
        start = non_transparent_cols[0]
        prev = start
        
        for col in non_transparent_cols[1:]:
            if col > prev + 1:  # Gap found
                regions.append((start, prev))
                start = col
            prev = col
        
        # Add the last region
        regions.append((start, prev))
    
    return regions

def calculate_dimensions(img, width, height, slices, direction="h"):
    """Calculate dimensions for each frame based on input parameters."""
    if direction == "h":
        img_width = img.width
        img_height = img.height
    else:
        # For vertical slicing, we conceptually rotate the image
        img_width = img.height
        img_height = img.width
    
    if width is not None:
        frame_width = width
        # If both width and height are specified, use them
        frame_height = height if height is not None else img_height
    elif slices is not None:
        # Divide image width by number of slices
        frame_width = img_width // slices
        frame_height = img_height
    else:
        raise ValueError("Either width or slices must be specified")
    
    return frame_width, frame_height

def slice_sprite(img, width=None, height=None, slices=None, direction="h", auto_detect=True, padding=0, resize=None):
    """Slice the image into frames based on parameters."""
    frame_width, frame_height = calculate_dimensions(img, width, height, slices, direction)
    
    frames = []
    
    if auto_detect:
        # Use automatic detection of non-transparent regions
        regions = detect_transparent_regions(img, direction)
        
        if not regions:
            print("Warning: No non-transparent regions detected.")
            return frames
        
        for start, end in regions:
            if direction == "h":
                # For horizontal slicing, extract vertical slices
                frame = img.crop((start, 0, end + 1, img.height))
            else:
                # For vertical slicing, extract horizontal slices
                frame = img.crop((0, start, img.width, end + 1))
            
            # Apply padding if specified
            if padding > 0:
                padded_frame = Image.new('RGBA', 
                                       (frame.width + 2*padding, frame.height + 2*padding),
                                       (0, 0, 0, 0))
                padded_frame.paste(frame, (padding, padding))
                frame = padded_frame
            
            # Resize if specified
            if resize:
                frame = frame.resize(resize, Image.LANCZOS)
            
            frames.append(frame)
    else:
        # Use fixed size slicing based on parameters
        if direction == "h":
            for i in range(slices or (img.width // frame_width)):
                start_x = i * frame_width
                if start_x >= img.width:
                    break
                
                # Calculate end position, ensuring it doesn't exceed image dimensions
                end_x = min(start_x + frame_width, img.width)
                
                frame = img.crop((start_x, 0, end_x, frame_height))
                
                # Apply padding if specified
                if padding > 0:
                    padded_frame = Image.new('RGBA', 
                                           (frame.width + 2*padding, frame.height + 2*padding),
                                           (0, 0, 0, 0))
                    padded_frame.paste(frame, (padding, padding))
                    frame = padded_frame
                
                # Resize if specified
                if resize:
                    frame = frame.resize(resize, Image.LANCZOS)
                
                frames.append(frame)
        else:
            for i in range(slices or (img.height // frame_width)):  # Using frame_width as the slice height
                start_y = i * frame_width
                if start_y >= img.height:
                    break
                
                # Calculate end position, ensuring it doesn't exceed image dimensions
                end_y = min(start_y + frame_width, img.height)
                
                frame = img.crop((0, start_y, frame_height, end_y))  # Using frame_height as width
                
                # Apply padding if specified
                if padding > 0:
                    padded_frame = Image.new('RGBA', 
                                           (frame.width + 2*padding, frame.height + 2*padding),
                                           (0, 0, 0, 0))
                    padded_frame.paste(frame, (padding, padding))
                    frame = padded_frame
                
                # Resize if specified
                if resize:
                    frame = frame.resize(resize, Image.LANCZOS)
                
                frames.append(frame)
    
    return frames

def save_frames(frames, output_dir, action_name, output_format='png', quality=90):
    """Save frames to specified directory with sequential naming."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    saved_files = []
    
    for i, frame in enumerate(frames):
        # Create filename: action_1.png, action_2.png, etc.
        filename = f"{action_name}_{i+1}.{output_format.lower()}"
        filepath = os.path.join(output_dir, filename)
        
        # Save with appropriate format and quality
        if output_format.lower() == 'png':
            frame.save(filepath, 'PNG')
        elif output_format.lower() == 'webp':
            frame.save(filepath, 'WEBP', quality=quality)
        elif output_format.lower() == 'gif':
            frame = frame.convert('RGBA')
            frame.save(filepath, 'GIF', quality=quality)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        saved_files.append(filepath)
    
    return saved_files

def process_image(image_path, args):
    """Process a single image according to the specified arguments."""
    try:
        # Open image
        img = Image.open(image_path)
        
        # Extract action name from filename (remove extension)
        action_name = os.path.splitext(os.path.basename(image_path))[0].lower()
        
        # Parse width and height
        width, height = None, None
        if args.width:
            width, height = parse_dimensions(args.width)
        
        # Parse resize dimensions if specified
        resize = None
        if args.resize:
            resize_width, resize_height = parse_dimensions(args.resize)
            resize = (resize_width, resize_height)
        
        # Slice the sprite
        frames = slice_sprite(
            img, 
            width=width, 
            height=height, 
            slices=args.slices, 
            direction=args.direction,
            auto_detect=args.auto_detect,
            padding=args.padding,
            resize=resize
        )
        
        if not frames:
            print(f"No frames extracted from {image_path}")
            return
        
        # Create output directory
        if args.output_dir:
            output_base = args.output_dir
        else:
            output_base = os.path.dirname(image_path) or '.'
        
        output_dir = os.path.join(output_base, action_name.lower())
        
        # Save frames
        saved_files = save_frames(
            frames, 
            output_dir, 
            action_name, 
            output_format=args.format, 
            quality=args.quality
        )
        
        print(f"Saved {len(saved_files)} frames from {image_path} to {output_dir}")
        
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Recorta sprites de animación para videojuegos.")
    
    parser.add_argument("input", help="Imagen o directorio a procesar")
    parser.add_argument("--width", help="Ancho de cada frame (o WIDTHxHEIGHT para especificar también el alto)")
    parser.add_argument("--slices", type=int, help="Número de divisiones a realizar")
    parser.add_argument("--direction", choices=["h", "v"], default="h", 
                        help="Dirección de corte (h=horizontal, v=vertical) [por defecto: h]")
    parser.add_argument("--output-dir", help="Directorio donde guardar los resultados")
    parser.add_argument("--format", choices=["png", "webp", "gif"], default="png",
                        help="Formato de salida [por defecto: png]")
    parser.add_argument("--quality", type=int, default=90, 
                        help="Calidad de la imagen (1-100) [por defecto: 90]")
    parser.add_argument("--padding", type=int, default=0,
                        help="Padding a añadir alrededor de cada frame [por defecto: 0]")
    parser.add_argument("--resize", help="Redimensionar frames (WIDTHxHEIGHT) [opcional]")
    parser.add_argument("--no-auto-detect", dest="auto_detect", action="store_false",
                        help="Desactivar la detección automática de zonas transparentes")
    
    # Set auto-detect to True by default
    parser.set_defaults(auto_detect=True)
    
    args = parser.parse_args()
    
    # Validate args
    if not args.width and not args.slices:
        parser.error("Debe especificar --width o --slices")
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: La ruta {input_path} no existe.")
        return 1
    
    # Process directory or single file
    if input_path.is_dir():
        image_extensions = ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.tiff']
        for file in input_path.iterdir():
            if file.suffix.lower() in image_extensions:
                process_image(file, args)
    else:
        process_image(input_path, args)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())