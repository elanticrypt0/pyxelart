#!/usr/bin/env python3
"""
Unit tests for utility modules
"""

import unittest
import numpy as np
from PIL import Image
import sys
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.sprite_utils import SpriteCutter
from utils.parallel_utils import ParallelProcessor, MemoryOptimizer, CacheManager


class TestSpriteCutter(unittest.TestCase):
    """Test SpriteCutter class"""

    def setUp(self):
        """Create test sprite sheet"""
        # Create a simple sprite sheet with 4 frames horizontally
        self.sprite_sheet = Image.new('RGBA', (200, 50), color=(0, 0, 0, 0))
        for i in range(4):
            # Draw a colored square for each frame
            for x in range(i*50, (i+1)*50):
                for y in range(50):
                    if 10 <= x % 50 <= 40 and 10 <= y <= 40:
                        self.sprite_sheet.putpixel((x, y), (255, 0, 0, 255))

    def test_parse_dimensions(self):
        """Test dimension parsing"""
        width, height = SpriteCutter.parse_dimensions("48x48")
        self.assertEqual(width, 48)
        self.assertEqual(height, 48)

        width, height = SpriteCutter.parse_dimensions("64")
        self.assertEqual(width, 64)
        self.assertIsNone(height)

    def test_slice_sprite_fixed(self):
        """Test fixed size slicing"""
        frames = SpriteCutter.slice_sprite(
            self.sprite_sheet,
            width=50,
            slices=4,
            auto_detect=False
        )
        self.assertEqual(len(frames), 4)
        for frame in frames:
            self.assertIsInstance(frame, Image.Image)

    def test_slice_with_padding(self):
        """Test slicing with padding"""
        frames = SpriteCutter.slice_sprite(
            self.sprite_sheet,
            width=50,
            slices=4,
            auto_detect=False,
            padding=5
        )
        self.assertEqual(len(frames), 4)
        # Frame should be larger due to padding
        self.assertEqual(frames[0].width, 60)

    def test_detect_transparent_regions(self):
        """Test transparent region detection"""
        regions = SpriteCutter.detect_transparent_regions(
            self.sprite_sheet, direction="h"
        )
        # Should detect 4 regions
        self.assertGreater(len(regions), 0)


class TestParallelProcessor(unittest.TestCase):
    """Test ParallelProcessor class"""

    def test_get_optimal_workers(self):
        """Test optimal worker calculation"""
        workers_io = ParallelProcessor.get_optimal_workers(io_bound=True)
        workers_cpu = ParallelProcessor.get_optimal_workers(io_bound=False)

        self.assertIsInstance(workers_io, int)
        self.assertIsInstance(workers_cpu, int)
        self.assertGreater(workers_io, 0)
        self.assertGreater(workers_cpu, 0)

    def test_process_batch_parallel(self):
        """Test parallel batch processing"""
        def dummy_func(x):
            return x * 2

        items = [1, 2, 3, 4, 5]
        results = ParallelProcessor.process_batch_parallel(
            items,
            dummy_func,
            max_workers=2,
            use_threading=True,
            show_progress=False
        )

        self.assertEqual(len(results), 5)
        self.assertIn(2, results)
        self.assertIn(10, results)

    def test_batch_process_images(self):
        """Test batch image processing"""
        # Create temp directories
        temp_dir = tempfile.mkdtemp()
        input_dir = Path(temp_dir) / "input"
        output_dir = Path(temp_dir) / "output"
        input_dir.mkdir()

        try:
            # Create test images
            for i in range(3):
                img = Image.new('RGB', (50, 50), color=(i*50, i*50, i*50))
                img.save(input_dir / f"test_{i}.png")

            # Define simple effect function
            def simple_effect(input_path, output_path):
                img = Image.open(input_path)
                img.save(output_path)
                return output_path

            # Process batch
            results = ParallelProcessor.batch_process_images(
                str(input_dir),
                str(output_dir),
                simple_effect,
                max_workers=2
            )

            # Check results
            self.assertEqual(len(results), 3)
            self.assertTrue(output_dir.exists())

        finally:
            shutil.rmtree(temp_dir)


class TestMemoryOptimizer(unittest.TestCase):
    """Test MemoryOptimizer class"""

    def test_get_optimal_preview_size(self):
        """Test preview size calculation"""
        # Large image
        size = MemoryOptimizer.get_optimal_preview_size((2000, 1500), max_dimension=800)
        self.assertLessEqual(max(size), 800)

        # Small image (should stay same)
        size = MemoryOptimizer.get_optimal_preview_size((400, 300), max_dimension=800)
        self.assertEqual(size, (400, 300))

    def test_create_preview(self):
        """Test preview creation"""
        img = Image.new('RGB', (2000, 1500), color=(128, 128, 128))
        preview = MemoryOptimizer.create_preview(img, max_dimension=800)

        self.assertIsInstance(preview, Image.Image)
        self.assertLessEqual(max(preview.size), 800)


class TestCacheManager(unittest.TestCase):
    """Test CacheManager class"""

    def test_cache_basic(self):
        """Test basic cache operations"""
        cache = CacheManager(max_size=3)

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        self.assertEqual(cache.get("key1"), "value1")
        self.assertEqual(cache.get("key2"), "value2")
        self.assertIsNone(cache.get("key3"))

    def test_cache_lru(self):
        """Test LRU eviction"""
        cache = CacheManager(max_size=2)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1

        self.assertIsNone(cache.get("key1"))
        self.assertEqual(cache.get("key2"), "value2")
        self.assertEqual(cache.get("key3"), "value3")

    def test_generate_key(self):
        """Test key generation"""
        cache = CacheManager()

        key1 = cache.generate_key("arg1", "arg2", param1="val1")
        key2 = cache.generate_key("arg1", "arg2", param1="val1")
        key3 = cache.generate_key("arg1", "arg3", param1="val1")

        self.assertEqual(key1, key2)
        self.assertNotEqual(key1, key3)

    def test_cache_clear(self):
        """Test cache clearing"""
        cache = CacheManager()

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()

        self.assertIsNone(cache.get("key1"))
        self.assertIsNone(cache.get("key2"))


if __name__ == '__main__':
    unittest.main()
