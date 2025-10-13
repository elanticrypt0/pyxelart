#!/usr/bin/env python3
"""
Aspect ratio utilities for PyxelArt
Centralized aspect ratio transformations
"""

from PIL import Image
import cv2
import numpy as np
from typing import Union, Tuple, Optional


class AspectRatioManager:
    """Manager for aspect ratio transformations"""
    
    # Predefined aspect ratios
    ASPECT_RATIOS = {
        '4:3': 4 / 3,
        '1:1': 1.0,
        '16:9': 16 / 9,
        '3:2': 3 / 2,
        '5:4': 5 / 4,
        '2:3': 2 / 3,  # Portrait 3:2
        '3:4': 3 / 4,  # Portrait 4:3
        '9:16': 9 / 16,  # Portrait 16:9
        'original': None
    }
    
    @staticmethod
    def parse_aspect_ratio(aspect_str: str) -> Optional[float]:
        """
        Parse aspect ratio string to numeric value
        
        Args:
            aspect_str: Aspect ratio string (e.g., '4:3', '1:1', 'original')
        
        Returns:
            float: Aspect ratio value or None for original
        """
        if aspect_str is None or aspect_str.lower() == 'original':
            return None
        
        aspect_str = aspect_str.strip()
        
        # Check predefined ratios
        if aspect_str in AspectRatioManager.ASPECT_RATIOS:
            return AspectRatioManager.ASPECT_RATIOS[aspect_str]
        
        # Try to parse custom ratio (e.g., "16:10")
        if ':' in aspect_str:
            try:
                width_str, height_str = aspect_str.split(':')
                width = float(width_str.strip())
                height = float(height_str.strip())
                if height != 0:
                    return width / height
            except ValueError:
                pass
        
        # Try to parse as decimal (e.g., "1.5")
        try:
            return float(aspect_str)
        except ValueError:
            pass
        
        raise ValueError(f"Invalid aspect ratio format: {aspect_str}")
    
    @staticmethod
    def apply_to_image(img: Image.Image, target_ratio: float, method: str = 'resize') -> Image.Image:
        """
        Apply aspect ratio transformation to PIL Image
        
        Args:
            img: PIL Image object
            target_ratio: Target aspect ratio (width/height)
            method: 'resize' to stretch, 'crop' to crop, 'pad' to add padding
        
        Returns:
            PIL Image with applied aspect ratio
        """
        if target_ratio is None:
            return img
        
        width, height = img.size
        current_ratio = width / height
        
        # If already at target ratio (within tolerance), return original
        if abs(current_ratio - target_ratio) < 0.01:
            return img
        
        if method == 'resize':
            return AspectRatioManager._resize_image(img, target_ratio)
        elif method == 'crop':
            return AspectRatioManager._crop_image(img, target_ratio)
        elif method == 'pad':
            return AspectRatioManager._pad_image(img, target_ratio)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    @staticmethod
    def apply_to_frame(frame: np.ndarray, target_ratio: float, method: str = 'resize') -> np.ndarray:
        """
        Apply aspect ratio transformation to OpenCV frame
        
        Args:
            frame: OpenCV frame (numpy array)
            target_ratio: Target aspect ratio (width/height)
            method: 'resize' to stretch, 'crop' to crop
        
        Returns:
            OpenCV frame with applied aspect ratio
        """
        if target_ratio is None:
            return frame
        
        height, width = frame.shape[:2]
        current_ratio = width / height
        
        # If already at target ratio (within tolerance), return original
        if abs(current_ratio - target_ratio) < 0.01:
            return frame
        
        if method == 'resize':
            return AspectRatioManager._resize_frame(frame, target_ratio)
        elif method == 'crop':
            return AspectRatioManager._crop_frame(frame, target_ratio)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    @staticmethod
    def _resize_image(img: Image.Image, target_ratio: float) -> Image.Image:
        """Resize image to target aspect ratio"""
        width, height = img.size
        
        # Calculate new dimensions maintaining height
        new_width = int(height * target_ratio)
        if new_width <= 0:
            new_width = 1
        
        return img.resize((new_width, height), Image.Resampling.LANCZOS)
    
    @staticmethod
    def _crop_image(img: Image.Image, target_ratio: float) -> Image.Image:
        """Crop image to target aspect ratio"""
        width, height = img.size
        current_ratio = width / height
        
        if current_ratio > target_ratio:
            # Image is wider than target, crop horizontally
            new_width = int(height * target_ratio)
            x_offset = (width - new_width) // 2
            return img.crop((x_offset, 0, x_offset + new_width, height))
        else:
            # Image is taller than target, crop vertically
            new_height = int(width / target_ratio)
            y_offset = (height - new_height) // 2
            return img.crop((0, y_offset, width, y_offset + new_height))
    
    @staticmethod
    def _pad_image(img: Image.Image, target_ratio: float, 
                   bg_color: Union[str, Tuple[int, int, int]] = 'black') -> Image.Image:
        """Pad image to target aspect ratio"""
        width, height = img.size
        current_ratio = width / height
        
        if current_ratio > target_ratio:
            # Image is wider than target, add padding vertically
            new_height = int(width / target_ratio)
            padding = (new_height - height) // 2
            
            # Create new image with padding
            if img.mode == 'RGBA':
                new_img = Image.new('RGBA', (width, new_height), (0, 0, 0, 0))
            else:
                if bg_color == 'black':
                    bg_color = (0, 0, 0)
                elif bg_color == 'white':
                    bg_color = (255, 255, 255)
                new_img = Image.new(img.mode, (width, new_height), bg_color)
            
            new_img.paste(img, (0, padding))
            return new_img
        else:
            # Image is taller than target, add padding horizontally
            new_width = int(height * target_ratio)
            padding = (new_width - width) // 2
            
            # Create new image with padding
            if img.mode == 'RGBA':
                new_img = Image.new('RGBA', (new_width, height), (0, 0, 0, 0))
            else:
                if bg_color == 'black':
                    bg_color = (0, 0, 0)
                elif bg_color == 'white':
                    bg_color = (255, 255, 255)
                new_img = Image.new(img.mode, (new_width, height), bg_color)
            
            new_img.paste(img, (padding, 0))
            return new_img
    
    @staticmethod
    def _resize_frame(frame: np.ndarray, target_ratio: float) -> np.ndarray:
        """Resize OpenCV frame to target aspect ratio"""
        height, width = frame.shape[:2]
        
        # Calculate new dimensions maintaining height
        new_width = int(height * target_ratio)
        if new_width <= 0:
            new_width = 1
        
        return cv2.resize(frame, (new_width, height), interpolation=cv2.INTER_LANCZOS4)
    
    @staticmethod
    def _crop_frame(frame: np.ndarray, target_ratio: float) -> np.ndarray:
        """Crop OpenCV frame to target aspect ratio"""
        height, width = frame.shape[:2]
        current_ratio = width / height
        
        if current_ratio > target_ratio:
            # Frame is wider than target, crop horizontally
            new_width = int(height * target_ratio)
            x_offset = (width - new_width) // 2
            return frame[:, x_offset:x_offset + new_width]
        else:
            # Frame is taller than target, crop vertically
            new_height = int(width / target_ratio)
            y_offset = (height - new_height) // 2
            return frame[y_offset:y_offset + new_height, :]
    
    @staticmethod
    def get_current_ratio(img_or_frame: Union[Image.Image, np.ndarray]) -> float:
        """Get current aspect ratio of image or frame"""
        if isinstance(img_or_frame, Image.Image):
            width, height = img_or_frame.size
        else:  # numpy array (OpenCV frame)
            height, width = img_or_frame.shape[:2]
        
        return width / height
    
    @staticmethod
    def calculate_dimensions(current_size: Tuple[int, int], target_ratio: float, 
                           method: str = 'resize') -> Tuple[int, int]:
        """
        Calculate new dimensions for aspect ratio transformation
        
        Args:
            current_size: Current (width, height)
            target_ratio: Target aspect ratio
            method: Transformation method
        
        Returns:
            tuple: New (width, height)
        """
        width, height = current_size
        current_ratio = width / height
        
        if abs(current_ratio - target_ratio) < 0.01:
            return current_size
        
        if method == 'resize':
            new_width = int(height * target_ratio)
            return (new_width, height)
        
        elif method == 'crop':
            if current_ratio > target_ratio:
                # Crop horizontally
                new_width = int(height * target_ratio)
                return (new_width, height)
            else:
                # Crop vertically
                new_height = int(width / target_ratio)
                return (width, new_height)
        
        elif method == 'pad':
            if current_ratio > target_ratio:
                # Pad vertically
                new_height = int(width / target_ratio)
                return (width, new_height)
            else:
                # Pad horizontally
                new_width = int(height * target_ratio)
                return (new_width, height)
        
        return current_size
    
    @staticmethod
    def get_supported_ratios() -> dict:
        """Get dictionary of supported aspect ratios"""
        return AspectRatioManager.ASPECT_RATIOS.copy()
    
    @staticmethod
    def is_landscape(img_or_frame: Union[Image.Image, np.ndarray]) -> bool:
        """Check if image/frame is landscape orientation"""
        ratio = AspectRatioManager.get_current_ratio(img_or_frame)
        return ratio > 1.0
    
    @staticmethod
    def is_portrait(img_or_frame: Union[Image.Image, np.ndarray]) -> bool:
        """Check if image/frame is portrait orientation"""
        ratio = AspectRatioManager.get_current_ratio(img_or_frame)
        return ratio < 1.0
    
    @staticmethod
    def is_square(img_or_frame: Union[Image.Image, np.ndarray], tolerance: float = 0.01) -> bool:
        """Check if image/frame is square (within tolerance)"""
        ratio = AspectRatioManager.get_current_ratio(img_or_frame)
        return abs(ratio - 1.0) < tolerance


# Convenience functions
def apply_aspect_ratio(img_or_frame: Union[Image.Image, np.ndarray], 
                      aspect_ratio: str, method: str = 'resize') -> Union[Image.Image, np.ndarray]:
    """
    Convenience function to apply aspect ratio
    
    Args:
        img_or_frame: PIL Image or OpenCV frame
        aspect_ratio: Aspect ratio string (e.g., '4:3', '1:1')
        method: Transformation method
    
    Returns:
        Transformed image or frame
    """
    target_ratio = AspectRatioManager.parse_aspect_ratio(aspect_ratio)
    
    if isinstance(img_or_frame, Image.Image):
        return AspectRatioManager.apply_to_image(img_or_frame, target_ratio, method)
    else:
        return AspectRatioManager.apply_to_frame(img_or_frame, target_ratio, method)

def parse_aspect_ratio(aspect_str: str) -> Optional[float]:
    """Convenience function to parse aspect ratio"""
    return AspectRatioManager.parse_aspect_ratio(aspect_str)