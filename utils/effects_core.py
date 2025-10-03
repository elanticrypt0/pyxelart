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

    @staticmethod
    def light_trail(img, intensity=50):
        """
        Apply light trail effect (moving lights simulation)

        Args:
            img: PIL Image object
            intensity: Effect amount (0-100)

        Returns:
            PIL Image with light trail effect
        """
        img_rgb = img.convert("RGB")
        normalized_effect = intensity / 100.0

        # 1. Gaussian blur
        blur_radius = 2 + (normalized_effect * 8)
        img_blurred = img_rgb.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        # 2. Layer overlay with offset
        num_layers = int(2 + (normalized_effect * 8))
        max_offset = int(5 + (normalized_effect * 20))

        result_img = np.array(img_blurred, dtype=np.float32)

        for i in range(num_layers):
            offset_x = int(max_offset * (i / (num_layers - 1) - 0.5) * 2)
            offset_y = int(max_offset * (i / (num_layers - 1) - 0.5) * 2)

            shifted_img = Image.new("RGB", img_rgb.size)
            shifted_img.paste(img_rgb, (offset_x, offset_y))

            alpha = 0.3 - (normalized_effect * 0.2)
            result_img = result_img * (1 - alpha) + np.array(shifted_img, dtype=np.float32) * alpha

        result_img = Image.fromarray(np.uint8(np.clip(result_img, 0, 255)))

        # 3. Add grain/noise
        noise_intensity = 2 + (normalized_effect * 8)
        noise = np.random.normal(0, noise_intensity, (img_rgb.height, img_rgb.width, 3))
        noisy_img_array = np.array(result_img, dtype=np.float32) + noise
        final_img = Image.fromarray(np.uint8(np.clip(noisy_img_array, 0, 255)))

        return final_img


class GlitchEffects:
    """Various glitch and distortion effects"""

    @staticmethod
    def glitch_blocks(img, intensity=10, block_size_min=10, block_size_max=50, seed=None):
        """
        Apply glitch effect by moving random blocks

        Args:
            img: PIL Image object
            intensity: Number of blocks to displace
            block_size_min: Minimum block side size
            block_size_max: Maximum block side size
            seed: Random seed for reproducibility

        Returns:
            PIL Image with block glitch effect
        """
        import random

        if seed is not None:
            random.seed(seed)

        img_copy = img.copy()
        width, height = img_copy.size

        for _ in range(intensity):
            actual_block_size_min = max(1, block_size_min)
            actual_block_size_max = max(actual_block_size_min, block_size_max)

            block_w = random.randint(actual_block_size_min, actual_block_size_max)
            block_h = random.randint(actual_block_size_min, actual_block_size_max)

            # Source block coordinates
            src_x = random.randint(0, max(0, width - block_w))
            src_y = random.randint(0, max(0, height - block_h))

            # Destination coordinates
            dst_x = random.randint(0, max(0, width - block_w))
            dst_y = random.randint(0, max(0, height - block_h))

            # Skip if invalid
            if block_w > width or block_h > height:
                continue
            if src_x + block_w > width or src_y + block_h > height:
                continue

            box = (src_x, src_y, src_x + block_w, src_y + block_h)
            region = img_copy.crop(box)
            img_copy.paste(region, (dst_x, dst_y))

        return img_copy

    @staticmethod
    def glitch_horizontal_shift(img, intensity=5, shift_height_min=5, shift_height_max=20,
                                max_offset=50, seed=None):
        """
        Apply glitch effect by shifting horizontal strips

        Args:
            img: PIL Image object
            intensity: Number of strips to shift
            shift_height_min: Minimum strip height
            shift_height_max: Maximum strip height
            max_offset: Maximum horizontal offset
            seed: Random seed for reproducibility

        Returns:
            PIL Image with horizontal shift glitch
        """
        import random

        if seed is not None:
            random.seed(seed)

        img_copy = img.copy()
        width, height = img_copy.size

        for _ in range(intensity):
            actual_shift_height_min = max(1, shift_height_min)
            actual_shift_height_max = max(actual_shift_height_min, shift_height_max)

            strip_height = random.randint(actual_shift_height_min, actual_shift_height_max)
            y_start = random.randint(0, max(0, height - strip_height))

            if strip_height == 0 or y_start + strip_height > height:
                continue

            box = (0, y_start, width, y_start + strip_height)
            strip = img_copy.crop(box)

            offset = random.randint(-max_offset, max_offset)
            shifted_strip = ImageChops.offset(strip, offset, 0)
            img_copy.paste(shifted_strip, (0, y_start))

        return img_copy

    @staticmethod
    def glitch_scanlines(img, intensity=0.1, line_height=1, line_color=(0, 0, 0, 100), seed=None):
        """
        Apply scanline glitch effect

        Args:
            img: PIL Image object
            intensity: Line density (0.0 to 1.0)
            line_height: Line thickness
            line_color: RGBA color tuple
            seed: Random seed for reproducibility

        Returns:
            PIL Image with scanline effect
        """
        import random

        if seed is not None:
            random.seed(seed)

        img_copy = img.copy()
        if img_copy.mode != 'RGBA':
            img_copy = img_copy.convert('RGBA')

        width, height = img_copy.size
        overlay = Image.new('RGBA', img_copy.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        for y in range(0, height, line_height * 2):
            if random.random() < intensity:
                draw.line([(0, y), (width, y)], fill=line_color, width=line_height)

        img_with_scanlines = Image.alpha_composite(img_copy, overlay)
        return img_with_scanlines


class PointillistEffect:
    """Pointillist/stippling artistic effect"""

    @staticmethod
    def apply(img, dot_size=6, spacing_ratio=1.2, color_sample_mode='direct',
              bg_color='white', jitter_strength=0.2):
        """
        Apply pointillist effect to image

        Args:
            img: PIL Image object
            dot_size: Size of dots (diameter)
            spacing_ratio: Spacing between dots relative to dot_size
            color_sample_mode: 'direct' or 'average' color sampling
            bg_color: Background color (color name, hex, or 'transparent')
            jitter_strength: Random position variation (0.0 to 1.0)

        Returns:
            PIL Image with pointillist effect
        """
        import random
        from PIL import ImageStat

        output_mode = 'RGB'
        if bg_color.lower() == 'transparent' or img.mode == 'RGBA':
            output_mode = 'RGBA'

        img_for_sampling = img.convert(output_mode if output_mode == 'RGBA' else 'RGB')

        bg_color_parsed = PointillistEffect._parse_background_color(bg_color, output_mode)
        output_img = Image.new(output_mode, img.size, bg_color_parsed)
        draw = ImageDraw.Draw(output_img)

        width, height = img.size
        radius = dot_size // 2
        step = max(1, int(dot_size * spacing_ratio))

        for y in range(0, height, step):
            for x in range(0, width, step):
                center_x = x + random.uniform(-jitter_strength, jitter_strength) * step
                center_y = y + random.uniform(-jitter_strength, jitter_strength) * step
                sample_x = int(max(0, min(center_x, width - 1)))
                sample_y = int(max(0, min(center_y, height - 1)))

                dot_color = None
                if color_sample_mode == 'direct':
                    dot_color = img_for_sampling.getpixel((sample_x, sample_y))
                elif color_sample_mode == 'average':
                    avg_box_left = max(0, sample_x - radius)
                    avg_box_top = max(0, sample_y - radius)
                    avg_box_right = min(width, sample_x + radius + 1)
                    avg_box_bottom = min(height, sample_y + radius + 1)

                    if avg_box_left < avg_box_right and avg_box_top < avg_box_bottom:
                        region = img_for_sampling.crop((avg_box_left, avg_box_top, avg_box_right, avg_box_bottom))
                        if region.size[0] > 0 and region.size[1] > 0:
                            try:
                                stat = ImageStat.Stat(region)
                                mean_values = stat.mean[:len(img_for_sampling.mode)]
                                dot_color = tuple(int(c) for c in mean_values)
                            except Exception:
                                dot_color = img_for_sampling.getpixel((sample_x, sample_y))
                        else:
                            dot_color = img_for_sampling.getpixel((sample_x, sample_y))
                    else:
                        dot_color = img_for_sampling.getpixel((sample_x, sample_y))

                if dot_color:
                    # Ensure correct color channels
                    if output_mode == 'RGB' and len(dot_color) == 4:
                        dot_color = dot_color[:3]
                    elif output_mode == 'RGBA' and len(dot_color) == 3:
                        dot_color = dot_color + (255,)

                    draw_x0 = center_x - radius
                    draw_y0 = center_y - radius
                    draw_x1 = center_x + radius
                    draw_y1 = center_y + radius
                    draw.ellipse([draw_x0, draw_y0, draw_x1, draw_y1], fill=dot_color)

        return output_img

    @staticmethod
    def _parse_background_color(color_str, target_mode='RGB'):
        """Parse background color string"""
        if color_str.lower() == 'transparent':
            if target_mode == 'RGBA':
                return (0, 0, 0, 0)
            else:
                return (255, 255, 255)

        if color_str.startswith('#'):
            try:
                return PointillistEffect._hex_to_rgb(color_str)
            except ValueError:
                return (255, 255, 255)

        return color_str

    @staticmethod
    def _hex_to_rgb(hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = "".join([c * 2 for c in hex_color])
        if len(hex_color) != 6:
            raise ValueError("Invalid hex color input")
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


class TextureEffects:
    """Texture and canvas simulation effects"""

    @staticmethod
    def canvas_texture(img, intensity=50):
        """
        Apply canvas texture effect

        Args:
            img: PIL Image object
            intensity: Effect intensity (0-100)

        Returns:
            PIL Image with canvas texture
        """
        img_rgb = img.convert("RGB")
        normalized_effect = intensity / 100.0

        # 1. Subtle blur to reduce fine details
        blur_radius = 1 + (normalized_effect * 2)
        img_blurred = img_rgb.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        # 2. Add subtle grain/noise
        noise_intensity = 2 + (normalized_effect * 5)
        noise = np.random.normal(0, noise_intensity, (img_rgb.height, img_rgb.width, 3))
        noisy_img_array = np.array(img_blurred, dtype=np.float32) + noise
        img_with_noise = Image.fromarray(np.uint8(np.clip(noisy_img_array, 0, 255)))

        # 3. Overlay with simulated canvas texture
        fractal_noise = TextureEffects._generate_fractal_noise(
            img_rgb.size, scale=8.0, octaves=6, persistence=0.5, lacunarity=2.0
        )
        noise_img = Image.fromarray(np.uint8(fractal_noise * 255)).convert("L")

        texture_opacity = 0.1 + (normalized_effect * 0.2)
        final_img = Image.blend(img_with_noise, noise_img.convert("RGB"), texture_opacity)

        return final_img

    @staticmethod
    def _generate_fractal_noise(size, scale=8.0, octaves=6, persistence=0.5, lacunarity=2.0):
        """Generate fractal noise for texture"""
        shape_for_noise_gen = (size[1], size[0])

        def fbm_2d(shape, base_frequency, frequencies, amplitudes):
            grid = np.mgrid[tuple(slice(0, dim, 1j * num) for dim, num in zip(shape, shape))]
            sample = np.zeros(shape)
            for i in range(len(frequencies)):
                frequency = frequencies[i]
                amplitude = amplitudes[i]
                sample += amplitude * np.sin(np.pi * base_frequency * frequency * grid).prod(0)
            return sample

        frequencies = [scale * (lacunarity ** i) for i in range(octaves)]
        amplitudes = [persistence ** i for i in range(octaves)]
        noise = fbm_2d(shape_for_noise_gen, 1.0, frequencies, amplitudes)
        return (noise + 1) / 2