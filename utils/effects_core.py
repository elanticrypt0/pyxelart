#!/usr/bin/env python3
"""
Core effects module for PyxelArt
Centralized implementation of main visual effects
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter
import cv2
import os


class PixelArtEffect:
    """Main pixel art effect with color reduction and pixelation"""
    
    @staticmethod
    def apply(img, colors=16, pixel_size=4, add_noise=True, noise_intensity=15):
        """
        Apply pixel art effect to an image
        
        Args:
            img: PIL Image object
            colors: Number of colors to reduce to (default: 16)
            pixel_size: Pixelation size (default: 4)
            add_noise: Whether to add noise (default: True)
            noise_intensity: Intensity of noise (default: 15)
        
        Returns:
            PIL Image with pixel art effect applied
        """
        # Preserve original alpha channel
        has_alpha = img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)
        alpha_channel = None
        
        if has_alpha:
            if img.mode == 'RGBA':
                alpha_channel = img.split()[-1]
            elif img.mode == 'LA':
                alpha_channel = img.split()[1]
            elif img.mode == 'P' and 'transparency' in img.info:
                img = img.convert('RGBA')
                alpha_channel = img.split()[-1]
        
        # Convert to RGB for processing
        if img.mode != 'RGB':
            img_rgb = img.convert('RGB')
        else:
            img_rgb = img
        
        # Apply color reduction using median cut quantization
        img_quantized = img_rgb.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
        img_reduced = img_quantized.convert('RGB')
        
        # Apply pixelation
        width, height = img_reduced.size
        
        # Scale down
        small_width = max(1, width // pixel_size)
        small_height = max(1, height // pixel_size)
        img_small = img_reduced.resize((small_width, small_height), Image.NEAREST)
        
        # Scale back up
        img_pixelated = img_small.resize((width, height), Image.NEAREST)
        
        # Add noise if requested
        if add_noise:
            img_pixelated = PixelArtEffect._add_noise(img_pixelated, noise_intensity)
        
        # Restore alpha channel if present
        if has_alpha and alpha_channel:
            img_pixelated = img_pixelated.convert('RGBA')
            img_pixelated.putalpha(alpha_channel)
        
        return img_pixelated
    
    @staticmethod
    def _add_noise(img, intensity):
        """Add gaussian noise to image"""
        np_img = np.array(img)
        shape = np_img.shape
        
        # Generate noise
        noise = np.random.randint(0, intensity, shape)
        
        # Apply noise
        np_img = np.clip(np_img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        return Image.fromarray(np_img)
    
    @staticmethod
    def apply_to_frame(frame, colors=16, pixel_size=4, add_noise=True, noise_intensity=15):
        """
        Apply pixel art effect to OpenCV frame (for video processing)
        
        Args:
            frame: OpenCV frame (BGR format)
            colors: Number of colors to reduce to
            pixel_size: Pixelation size
            add_noise: Whether to add noise
            noise_intensity: Intensity of noise
        
        Returns:
            OpenCV frame with pixel art effect applied
        """
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_img = Image.fromarray(frame_rgb)
        
        # Apply effect
        processed_img = PixelArtEffect.apply(pil_img, colors, pixel_size, add_noise, noise_intensity)
        
        # Convert back to OpenCV format
        processed_frame = np.array(processed_img)
        frame_bgr = cv2.cvtColor(processed_frame, cv2.COLOR_RGB2BGR)
        
        return frame_bgr


class ChromaticAberration:
    """Chromatic aberration effect"""
    
    @staticmethod
    def apply(img, intensity=1.0, red_shift=(2, 0), green_shift=(0, 0), blue_shift=(-2, 0), 
              lens_effect=False, lens_center=None, lens_falloff='quadratic', edge_mode='transparent'):
        """
        Apply chromatic aberration effect
        
        Args:
            img: PIL Image object
            intensity: Overall intensity multiplier
            red_shift: (x, y) shift for red channel
            green_shift: (x, y) shift for green channel  
            blue_shift: (x, y) shift for blue channel
            lens_effect: Apply lens distortion
            lens_center: Center point for lens effect
            lens_falloff: 'quadratic' or 'linear'
            edge_mode: 'transparent', 'black', 'white', 'clamp'
        
        Returns:
            PIL Image with chromatic aberration applied
        """
        # Handle different modes
        has_alpha = img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)
        
        if img.mode == 'RGBA':
            r, g, b, a = img.split()
        elif img.mode == 'RGB':
            r, g, b = img.split()
            a = None
        else:
            img = img.convert('RGB')
            r, g, b = img.split()
            a = None
        
        width, height = img.size
        
        # Apply lens effect if requested
        if lens_effect:
            if lens_center is None:
                lens_center = (width // 2, height // 2)
            
            r = ChromaticAberration._apply_lens_distortion(r, lens_center, intensity, lens_falloff)
            g = ChromaticAberration._apply_lens_distortion(g, lens_center, intensity, lens_falloff)
            b = ChromaticAberration._apply_lens_distortion(b, lens_center, intensity, lens_falloff)
        
        # Apply channel shifts
        r_shifted = ChromaticAberration._shift_channel(r, red_shift, intensity, edge_mode)
        g_shifted = ChromaticAberration._shift_channel(g, green_shift, intensity, edge_mode)
        b_shifted = ChromaticAberration._shift_channel(b, blue_shift, intensity, edge_mode)
        
        # Merge channels
        if has_alpha and a:
            result = Image.merge('RGBA', (r_shifted, g_shifted, b_shifted, a))
        else:
            result = Image.merge('RGB', (r_shifted, g_shifted, b_shifted))
        
        return result
    
    @staticmethod
    def _shift_channel(channel, shift, intensity, edge_mode):
        """Shift a single channel"""
        offset_x = int(shift[0] * intensity)
        offset_y = int(shift[1] * intensity)
        
        if offset_x == 0 and offset_y == 0:
            return channel
        
        if edge_mode == 'transparent':
            # Create transparent background
            shifted = Image.new('L', channel.size, 0)
            shifted.paste(channel, (offset_x, offset_y))
            return shifted
        elif edge_mode == 'black':
            return ImageChops.offset(channel, offset_x, offset_y)
        elif edge_mode == 'white':
            shifted = Image.new('L', channel.size, 255)
            shifted.paste(channel, (offset_x, offset_y))
            return shifted
        elif edge_mode == 'clamp':
            # Clamp to edges (more complex implementation)
            return ImageChops.offset(channel, offset_x, offset_y)
        
        return channel
    
    @staticmethod
    def _apply_lens_distortion(channel, center, intensity, falloff):
        """Apply lens distortion to a channel"""
        width, height = channel.size
        cx, cy = center
        
        # Create coordinate grids
        x, y = np.meshgrid(np.arange(width), np.arange(height))
        
        # Calculate distance from center
        dx = x - cx
        dy = y - cy
        distance = np.sqrt(dx**2 + dy**2)
        
        # Normalize distance
        max_distance = np.sqrt(cx**2 + cy**2)
        normalized_distance = distance / max_distance
        
        # Apply falloff
        if falloff == 'quadratic':
            distortion = normalized_distance**2 * intensity
        else:  # linear
            distortion = normalized_distance * intensity
        
        # Apply distortion (simplified version)
        return channel


class RetroDialog:
    """Retro-style dialog box effect"""
    
    @staticmethod
    def add_dialog(img, text, pixel_size=4, dialog_color=(0, 0, 0), 
                   text_color=(255, 255, 255), border_color=(255, 255, 255)):
        """
        Add retro dialog box to image
        
        Args:
            img: PIL Image object
            text: Text to display
            pixel_size: Size of pixels for retro effect
            dialog_color: Background color of dialog
            text_color: Text color
            border_color: Border color
        
        Returns:
            PIL Image with dialog box added
        """
        width, height = img.size
        dialog_height = pixel_size * 10
        
        # Create new canvas
        if img.mode == 'RGBA':
            canvas = Image.new('RGBA', (width, height + dialog_height), (0, 0, 0, 0))
        else:
            canvas = Image.new('RGB', (width, height + dialog_height), (0, 0, 0))
        
        # Paste original image
        canvas.paste(img, (0, 0))
        
        # Draw dialog box
        draw = ImageDraw.Draw(canvas)
        
        # Dialog box coordinates
        dialog_box = [0, height, width, height + dialog_height]
        
        # Draw background
        draw.rectangle(dialog_box, fill=dialog_color, outline=border_color, width=2)
        
        # Draw text
        try:
            # Try to use a bitmap font for retro look
            font_size = max(8, pixel_size * 2)
            font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Calculate text position (centered)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        text_x = (width - text_width) // 2
        text_y = height + (dialog_height - text_height) // 2
        
        draw.text((text_x, text_y), text, fill=text_color, font=font)
        
        return canvas


class NoiseGenerator:
    """Various noise generation utilities"""
    
    @staticmethod
    def gaussian_noise(img, intensity=15):
        """Add gaussian noise to image"""
        np_img = np.array(img)
        shape = np_img.shape
        
        # Generate noise
        noise = np.random.randint(0, intensity, shape)
        
        # Apply noise
        np_img = np.clip(np_img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        return Image.fromarray(np_img)
    
    @staticmethod
    def controlled_gaussian_noise(img, intensity=0.1):
        """Add controlled gaussian noise"""
        np_img = np.array(img)
        shape = np_img.shape
        
        # Generate noise
        noise = np.random.normal(0, intensity * 255, shape)
        
        # Apply noise
        np_img = np.clip(np_img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
        
        return Image.fromarray(np_img)
    
    @staticmethod
    def fractal_noise(width, height, octaves=4, persistence=0.5, lacunarity=2.0):
        """Generate fractal noise (simplified version)"""
        # This is a simplified implementation
        # For full fractal noise, you'd need a noise library like noise or opensimplex
        
        noise_map = np.zeros((height, width))
        
        for i in range(octaves):
            frequency = lacunarity ** i
            amplitude = persistence ** i
            
            # Generate simple noise for this octave
            octave_noise = np.random.random((height, width))
            
            # Apply frequency and amplitude
            noise_map += octave_noise * amplitude
        
        # Normalize to 0-255 range
        noise_map = ((noise_map - noise_map.min()) / (noise_map.max() - noise_map.min()) * 255).astype(np.uint8)
        
        return Image.fromarray(noise_map, mode='L')


class BlurEffects:
    """Various blur effects"""
    
    @staticmethod
    def gaussian_blur(img, radius=2.0):
        """Apply gaussian blur"""
        return img.filter(ImageFilter.GaussianBlur(radius=radius))
    
    @staticmethod
    def motion_blur(img, angle=0, distance=5):
        """Apply motion blur effect (simplified)"""
        # This is a simplified version
        # For proper motion blur, you'd need more complex kernel operations
        
        # Convert angle to radians
        angle_rad = np.radians(angle)
        
        # Calculate offset
        dx = int(distance * np.cos(angle_rad))
        dy = int(distance * np.sin(angle_rad))
        
        # Create blurred version by averaging shifted versions
        blurred = img.copy()
        
        for i in range(1, distance + 1):
            offset_x = int(dx * i / distance)
            offset_y = int(dy * i / distance)
            
            shifted = ImageChops.offset(img, offset_x, offset_y)
            blurred = ImageChops.blend(blurred, shifted, 0.5)
        
        return blurred