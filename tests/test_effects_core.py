#!/usr/bin/env python3
"""
Unit tests for effects_core module
"""

import unittest
import numpy as np
from PIL import Image
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.effects_core import (
    PixelArtEffect,
    ChromaticAberration,
    RetroDialog,
    NoiseGenerator,
    BlurEffects,
    GlitchEffects,
    PointillistEffect,
    TextureEffects
)


class TestPixelArtEffect(unittest.TestCase):
    """Test PixelArtEffect class"""

    def setUp(self):
        """Create test image"""
        self.img = Image.new('RGB', (100, 100), color=(128, 128, 128))

    def test_apply_basic(self):
        """Test basic pixel art effect"""
        result = PixelArtEffect.apply(self.img, colors=16, pixel_size=4)
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, self.img.size)

    def test_apply_with_noise(self):
        """Test pixel art with noise"""
        result = PixelArtEffect.apply(self.img, colors=8, add_noise=True, noise_intensity=20)
        self.assertIsInstance(result, Image.Image)

    def test_apply_no_noise(self):
        """Test pixel art without noise"""
        result = PixelArtEffect.apply(self.img, colors=8, add_noise=False)
        self.assertIsInstance(result, Image.Image)

    def test_alpha_preservation(self):
        """Test alpha channel preservation"""
        img_rgba = Image.new('RGBA', (100, 100), color=(128, 128, 128, 200))
        result = PixelArtEffect.apply(img_rgba, colors=16, pixel_size=4)
        self.assertEqual(result.mode, 'RGBA')


class TestChromaticAberration(unittest.TestCase):
    """Test ChromaticAberration class"""

    def setUp(self):
        """Create test image"""
        self.img = Image.new('RGB', (100, 100), color=(128, 128, 128))

    def test_apply_basic(self):
        """Test basic chromatic aberration"""
        result = ChromaticAberration.apply(self.img, intensity=1.5)
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, self.img.size)

    def test_apply_with_custom_shifts(self):
        """Test with custom channel shifts"""
        result = ChromaticAberration.apply(
            self.img,
            red_shift=(3, 0),
            green_shift=(0, 0),
            blue_shift=(-3, 0)
        )
        self.assertIsInstance(result, Image.Image)

    def test_lens_effect(self):
        """Test with lens effect"""
        result = ChromaticAberration.apply(self.img, lens_effect=True, intensity=2.0)
        self.assertIsInstance(result, Image.Image)


class TestGlitchEffects(unittest.TestCase):
    """Test GlitchEffects class"""

    def setUp(self):
        """Create test image"""
        self.img = Image.new('RGB', (200, 200), color=(128, 128, 128))

    def test_glitch_blocks(self):
        """Test block glitch effect"""
        result = GlitchEffects.glitch_blocks(self.img, intensity=10, seed=42)
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, self.img.size)

    def test_glitch_horizontal_shift(self):
        """Test horizontal shift glitch"""
        result = GlitchEffects.glitch_horizontal_shift(
            self.img, intensity=5, max_offset=20, seed=42
        )
        self.assertIsInstance(result, Image.Image)

    def test_glitch_scanlines(self):
        """Test scanline glitch"""
        result = GlitchEffects.glitch_scanlines(
            self.img, intensity=0.1, line_height=2, seed=42
        )
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.mode, 'RGBA')


class TestBlurEffects(unittest.TestCase):
    """Test BlurEffects class"""

    def setUp(self):
        """Create test image"""
        self.img = Image.new('RGB', (100, 100), color=(128, 128, 128))

    def test_gaussian_blur(self):
        """Test gaussian blur"""
        result = BlurEffects.gaussian_blur(self.img, radius=2.0)
        self.assertIsInstance(result, Image.Image)

    def test_motion_blur(self):
        """Test motion blur"""
        result = BlurEffects.motion_blur(self.img, angle=45, distance=5)
        self.assertIsInstance(result, Image.Image)

    def test_light_trail(self):
        """Test light trail effect"""
        result = BlurEffects.light_trail(self.img, intensity=50)
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.mode, 'RGB')


class TestPointillistEffect(unittest.TestCase):
    """Test PointillistEffect class"""

    def setUp(self):
        """Create test image"""
        self.img = Image.new('RGB', (100, 100), color=(128, 128, 128))

    def test_apply_direct_sampling(self):
        """Test pointillist with direct color sampling"""
        result = PointillistEffect.apply(
            self.img, dot_size=6, color_sample_mode='direct'
        )
        self.assertIsInstance(result, Image.Image)

    def test_apply_average_sampling(self):
        """Test pointillist with average color sampling"""
        result = PointillistEffect.apply(
            self.img, dot_size=8, color_sample_mode='average'
        )
        self.assertIsInstance(result, Image.Image)

    def test_hex_color_parsing(self):
        """Test hex color parsing"""
        rgb = PointillistEffect._hex_to_rgb('#FF5733')
        self.assertEqual(rgb, (255, 87, 51))


class TestTextureEffects(unittest.TestCase):
    """Test TextureEffects class"""

    def setUp(self):
        """Create test image"""
        self.img = Image.new('RGB', (100, 100), color=(128, 128, 128))

    def test_canvas_texture(self):
        """Test canvas texture effect"""
        result = TextureEffects.canvas_texture(self.img, intensity=50)
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.mode, 'RGB')

    def test_varying_intensity(self):
        """Test with varying intensity"""
        result_low = TextureEffects.canvas_texture(self.img, intensity=10)
        result_high = TextureEffects.canvas_texture(self.img, intensity=90)
        self.assertIsInstance(result_low, Image.Image)
        self.assertIsInstance(result_high, Image.Image)


class TestRetroDialog(unittest.TestCase):
    """Test RetroDialog class"""

    def setUp(self):
        """Create test image"""
        self.img = Image.new('RGB', (200, 100), color=(128, 128, 128))

    def test_add_dialog(self):
        """Test adding retro dialog"""
        result = RetroDialog.add_dialog(self.img, text="GAME OVER", pixel_size=4)
        self.assertIsInstance(result, Image.Image)
        # Dialog adds height to image
        self.assertGreater(result.height, self.img.height)


class TestNoiseGenerator(unittest.TestCase):
    """Test NoiseGenerator class"""

    def setUp(self):
        """Create test image"""
        self.img = Image.new('RGB', (100, 100), color=(128, 128, 128))

    def test_gaussian_noise(self):
        """Test gaussian noise"""
        result = NoiseGenerator.gaussian_noise(self.img, intensity=15)
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, self.img.size)

    def test_fractal_noise(self):
        """Test fractal noise generation"""
        result = NoiseGenerator.fractal_noise(100, 100, octaves=4)
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (100, 100))


if __name__ == '__main__':
    unittest.main()
