#!/usr/bin/env python3
"""
Format utilities for PyxelArt
Centralized format handling and image saving
"""

import os
from PIL import Image
from pathlib import Path


class FormatManager:
    """Centralized format and quality management"""
    
    # Supported formats
    SUPPORTED_IMAGE_FORMATS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')
    SUPPORTED_VIDEO_FORMATS = ('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv')
    SUPPORTED_AUDIO_FORMATS = ('.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a')
    
    # Default quality settings
    DEFAULT_QUALITY = {
        'jpeg': 95,
        'jpg': 95,
        'webp': 95,
        'png': 95,
        'tiff': 95
    }
    
    @staticmethod
    def get_save_options(format_name, quality=95, has_alpha=False):
        """
        Get save options for a specific format
        
        Args:
            format_name: Format name (e.g., 'png', 'jpg', 'webp')
            quality: Quality setting (1-100)
            has_alpha: Whether image has alpha channel
        
        Returns:
            Dictionary of save options for PIL Image.save()
        """
        format_name = format_name.lower()
        save_options = {}
        
        if format_name in ('jpg', 'jpeg'):
            save_options['quality'] = quality
            save_options['optimize'] = True
            if quality >= 95:
                save_options['subsampling'] = 0  # No subsampling for high quality
        
        elif format_name == 'png':
            save_options['optimize'] = True
            # Convert quality (1-100) to compression level (0-9)
            compression_level = min(9, max(0, 9 - int(quality / 11)))
            save_options['compress_level'] = compression_level
        
        elif format_name == 'webp':
            save_options['quality'] = quality
            save_options['method'] = 6  # Better compression
            if quality == 100:
                save_options['lossless'] = True
            else:
                save_options['lossless'] = False
        
        elif format_name == 'tiff':
            save_options['compression'] = 'lzw'
            save_options['optimize'] = True
        
        elif format_name == 'bmp':
            # BMP doesn't support quality settings
            pass
        
        elif format_name == 'gif':
            save_options['optimize'] = True
            # For GIF, we might need palette optimization
            save_options['save_all'] = True
        
        return save_options
    
    @staticmethod
    def save_image(img, output_path, format_name=None, quality=95, optimize_for_web=False):
        """
        Save image with appropriate format settings
        
        Args:
            img: PIL Image object
            output_path: Output file path
            format_name: Format to save as (auto-detected from path if None)
            quality: Quality setting (1-100)
            optimize_for_web: Whether to optimize for web use
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Determine format from path if not specified
            if format_name is None:
                format_name = Path(output_path).suffix.lower().lstrip('.')
            
            # Handle alpha channel
            has_alpha = img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)
            
            # Convert image mode if necessary
            if format_name in ('jpg', 'jpeg') and has_alpha:
                # JPEG doesn't support alpha, convert to RGB with white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[3])  # Use alpha as mask
                else:
                    background.paste(img, (0, 0))
                img = background
            
            # Get save options
            save_options = FormatManager.get_save_options(format_name, quality, has_alpha)
            
            # Apply web optimization if requested
            if optimize_for_web:
                save_options['optimize'] = True
                if format_name in ('jpg', 'jpeg'):
                    save_options['progressive'] = True
                elif format_name == 'png':
                    save_options['compress_level'] = 9
            
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir:  # Only create if there's a directory part
                os.makedirs(output_dir, exist_ok=True)
            
            # Save the image
            img.save(output_path, **save_options)
            
            return True
            
        except Exception as e:
            print(f"Error saving image {output_path}: {e}")
            return False
    
    @staticmethod
    def get_output_format(input_path, output_path=None, preferred_format=None):
        """
        Determine output format based on input and preferences
        
        Args:
            input_path: Input file path
            output_path: Output file path (optional)
            preferred_format: Preferred output format (optional)
        
        Returns:
            str: Output format
        """
        if preferred_format:
            return preferred_format.lower()
        
        if output_path:
            return Path(output_path).suffix.lower().lstrip('.')
        
        # Default to input format
        return Path(input_path).suffix.lower().lstrip('.')
    
    @staticmethod
    def generate_output_path(input_path, output_dir=None, suffix='_processed', 
                           format_name=None, preserve_name=False):
        """
        Generate output path based on input path and parameters
        
        Args:
            input_path: Input file path
            output_dir: Output directory (optional)
            suffix: Suffix to add to filename
            format_name: Output format (optional)
            preserve_name: Whether to preserve original filename
        
        Returns:
            str: Generated output path
        """
        input_path = Path(input_path)
        
        # Determine output directory
        if output_dir:
            output_directory = Path(output_dir)
        else:
            output_directory = input_path.parent
        
        # Determine filename
        if preserve_name:
            filename = input_path.stem
        else:
            filename = input_path.stem + suffix
        
        # Determine extension
        if format_name:
            extension = f'.{format_name.lower()}'
        else:
            extension = input_path.suffix
        
        # Create full output path
        output_path = output_directory / (filename + extension)
        
        return str(output_path)
    
    @staticmethod
    def is_supported_image(file_path):
        """Check if file is a supported image format"""
        return Path(file_path).suffix.lower() in FormatManager.SUPPORTED_IMAGE_FORMATS
    
    @staticmethod
    def is_supported_video(file_path):
        """Check if file is a supported video format"""
        return Path(file_path).suffix.lower() in FormatManager.SUPPORTED_VIDEO_FORMATS
    
    @staticmethod
    def is_supported_audio(file_path):
        """Check if file is a supported audio format"""
        return Path(file_path).suffix.lower() in FormatManager.SUPPORTED_AUDIO_FORMATS
    
    @staticmethod
    def validate_quality(quality):
        """
        Validate and clamp quality value
        
        Args:
            quality: Quality value to validate
        
        Returns:
            int: Validated quality value (1-100)
        """
        try:
            quality = int(quality)
            return max(1, min(100, quality))
        except (ValueError, TypeError):
            return 95
    
    @staticmethod
    def get_default_quality(format_name):
        """Get default quality for a format"""
        format_name = format_name.lower()
        return FormatManager.DEFAULT_QUALITY.get(format_name, 95)
    
    @staticmethod
    def optimize_for_size(img, max_size_mb=5, quality_start=95):
        """
        Optimize image size by reducing quality
        
        Args:
            img: PIL Image object
            max_size_mb: Maximum size in MB
            quality_start: Starting quality
        
        Returns:
            tuple: (optimized_img, final_quality)
        """
        import io
        
        max_size_bytes = max_size_mb * 1024 * 1024
        current_quality = quality_start
        
        while current_quality > 10:
            # Test save with current quality
            buffer = io.BytesIO()
            save_options = FormatManager.get_save_options('jpeg', current_quality)
            img.save(buffer, format='JPEG', **save_options)
            
            if buffer.tell() <= max_size_bytes:
                break
            
            current_quality -= 10
        
        return img, current_quality
    
    @staticmethod
    def get_image_info(file_path):
        """
        Get information about an image file
        
        Args:
            file_path: Path to image file
        
        Returns:
            dict: Image information
        """
        try:
            with Image.open(file_path) as img:
                info = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'has_alpha': img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info),
                    'file_size': os.path.getsize(file_path),
                    'is_animated': hasattr(img, 'is_animated') and img.is_animated
                }
                return info
        except Exception as e:
            return {'error': str(e)}


class VideoFormatManager:
    """Video format utilities"""
    
    @staticmethod
    def get_ffmpeg_codec(format_name):
        """Get appropriate FFmpeg codec for format"""
        format_name = format_name.lower()
        
        codecs = {
            'mp4': 'libx264',
            'avi': 'libxvid',
            'mov': 'libx264',
            'mkv': 'libx264',
            'webm': 'libvpx-vp9',
            'flv': 'libx264',
            'wmv': 'wmv2'
        }
        
        return codecs.get(format_name, 'libx264')
    
    @staticmethod
    def get_ffmpeg_quality_params(quality=23, preset='medium'):
        """Get FFmpeg quality parameters"""
        # CRF values: 0-51 (lower is better quality)
        quality = max(0, min(51, quality))
        
        return {
            'crf': str(quality),
            'preset': preset
        }


class AudioFormatManager:
    """Audio format utilities"""
    
    @staticmethod
    def get_ffmpeg_audio_codec(format_name):
        """Get appropriate FFmpeg audio codec for format"""
        format_name = format_name.lower()
        
        codecs = {
            'mp3': 'libmp3lame',
            'wav': 'pcm_s16le',
            'aac': 'aac',
            'flac': 'flac',
            'ogg': 'libvorbis',
            'm4a': 'aac'
        }
        
        return codecs.get(format_name, 'libmp3lame')
    
    @staticmethod
    def get_audio_quality_params(format_name, bitrate='192k'):
        """Get audio quality parameters"""
        format_name = format_name.lower()
        
        if format_name == 'mp3':
            return ['-b:a', bitrate]
        elif format_name == 'aac':
            return ['-b:a', bitrate]
        elif format_name == 'ogg':
            return ['-q:a', '6']  # Quality level for Vorbis
        elif format_name == 'flac':
            return ['-compression_level', '8']
        elif format_name == 'wav':
            return []  # No compression options for WAV
        else:
            return ['-b:a', bitrate]