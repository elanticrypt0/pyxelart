#!/usr/bin/env python3
"""
Parallel processing utilities for PyxelArt
Provides tools for batch processing optimization
"""

import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count
from PIL import Image
from pathlib import Path
from tqdm import tqdm


class ParallelProcessor:
    """Parallel processing utilities for batch operations"""

    @staticmethod
    def get_optimal_workers(io_bound=True):
        """
        Get optimal number of workers

        Args:
            io_bound: True for I/O bound tasks, False for CPU bound

        Returns:
            Optimal number of workers
        """
        cpu_cores = cpu_count()
        if io_bound:
            # I/O bound: more workers (2-4x CPU cores)
            return min(cpu_cores * 2, 32)
        else:
            # CPU bound: use CPU cores - 1 (leave one for system)
            return max(cpu_cores - 1, 1)

    @staticmethod
    def process_batch_parallel(file_paths, process_func, max_workers=None,
                              use_threading=False, show_progress=True,
                              description="Processing"):
        """
        Process files in parallel

        Args:
            file_paths: List of file paths to process
            process_func: Function to apply to each file (must accept file_path as first arg)
            max_workers: Number of workers (None for auto)
            use_threading: Use threads instead of processes
            show_progress: Show progress bar
            description: Progress bar description

        Returns:
            List of results
        """
        if max_workers is None:
            max_workers = ParallelProcessor.get_optimal_workers(io_bound=use_threading)

        ExecutorClass = ThreadPoolExecutor if use_threading else ProcessPoolExecutor
        results = []

        with ExecutorClass(max_workers=max_workers) as executor:
            futures = {executor.submit(process_func, fp): fp for fp in file_paths}

            if show_progress:
                progress = tqdm(total=len(file_paths), desc=description)

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    file_path = futures[future]
                    print(f"Error processing {file_path}: {e}")
                    results.append(None)

                if show_progress:
                    progress.update(1)

            if show_progress:
                progress.close()

        return results

    @staticmethod
    def batch_process_images(input_dir, output_dir, effect_func, file_pattern="*",
                            max_workers=None, create_output_dir=True):
        """
        Process directory of images with an effect function

        Args:
            input_dir: Input directory path
            output_dir: Output directory path
            effect_func: Function that takes (input_path, output_path) and applies effect
            file_pattern: Glob pattern for files
            max_workers: Number of workers
            create_output_dir: Auto-create output directory

        Returns:
            List of processed file paths
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)

        if create_output_dir:
            output_path.mkdir(parents=True, exist_ok=True)

        # Find all image files
        image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff'}
        file_paths = [
            f for f in input_path.glob(file_pattern)
            if f.suffix.lower() in image_extensions
        ]

        def process_single(input_file):
            output_file = output_path / input_file.name
            return effect_func(str(input_file), str(output_file))

        return ParallelProcessor.process_batch_parallel(
            file_paths,
            process_single,
            max_workers=max_workers,
            use_threading=True,
            description="Processing images"
        )


class MemoryOptimizer:
    """Memory optimization utilities"""

    @staticmethod
    def get_optimal_preview_size(original_size, max_dimension=800):
        """
        Calculate optimal preview size

        Args:
            original_size: Tuple (width, height)
            max_dimension: Maximum dimension for preview

        Returns:
            Tuple (width, height) for preview
        """
        width, height = original_size

        if max(width, height) <= max_dimension:
            return original_size

        if width > height:
            scale = max_dimension / width
        else:
            scale = max_dimension / height

        new_width = int(width * scale)
        new_height = int(height * scale)

        return (new_width, new_height)

    @staticmethod
    def create_preview(img, max_dimension=800):
        """
        Create memory-efficient preview

        Args:
            img: PIL Image
            max_dimension: Maximum dimension

        Returns:
            Resized PIL Image for preview
        """
        preview_size = MemoryOptimizer.get_optimal_preview_size(
            img.size, max_dimension
        )

        if preview_size == img.size:
            return img.copy()

        return img.resize(preview_size, Image.Resampling.LANCZOS)

    @staticmethod
    def process_large_image_chunked(img, effect_func, chunk_size=1024):
        """
        Process large image in chunks to save memory

        Args:
            img: PIL Image
            effect_func: Function to apply (must work on PIL Image)
            chunk_size: Size of chunks

        Returns:
            Processed PIL Image
        """
        width, height = img.size

        # If image is small enough, process normally
        if max(width, height) <= chunk_size * 2:
            return effect_func(img)

        # Otherwise process in chunks
        # Note: This is a simplified version - some effects may not work well with chunking
        # For now, just process the whole image but warn about memory
        print(f"Warning: Processing large image ({width}x{height}). This may use significant memory.")
        return effect_func(img)


class CacheManager:
    """Simple cache for effect previews"""

    def __init__(self, max_size=50):
        """
        Initialize cache

        Args:
            max_size: Maximum number of cached items
        """
        self.cache = {}
        self.max_size = max_size
        self.access_order = []

    def get(self, key):
        """Get cached item"""
        if key in self.cache:
            # Update access order
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None

    def set(self, key, value):
        """Cache an item"""
        if key in self.cache:
            # Update existing
            self.access_order.remove(key)
        elif len(self.cache) >= self.max_size:
            # Remove least recently used
            lru_key = self.access_order.pop(0)
            del self.cache[lru_key]

        self.cache[key] = value
        self.access_order.append(key)

    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.access_order.clear()

    def generate_key(self, *args, **kwargs):
        """
        Generate cache key from arguments

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            String cache key
        """
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return "|".join(key_parts)
