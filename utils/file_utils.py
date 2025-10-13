#!/usr/bin/env python3
"""
File utilities for PyxelArt
Centralized file and directory processing
"""

import os
import shutil
from pathlib import Path
from typing import List, Generator, Optional, Callable, Any
from tqdm import tqdm


class FileProcessor:
    """Base class for file processing operations"""
    
    def __init__(self, supported_extensions: List[str], progress_desc: str = "Processing files"):
        self.supported_extensions = [ext.lower() for ext in supported_extensions]
        self.progress_desc = progress_desc
    
    def is_supported_file(self, file_path: Path) -> bool:
        """Check if file is supported"""
        return file_path.suffix.lower() in self.supported_extensions
    
    def find_files(self, directory: Path, recursive: bool = False) -> List[Path]:
        """Find all supported files in directory"""
        files = []
        
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and self.is_supported_file(file_path):
                files.append(file_path)
        
        return sorted(files)
    
    def process_directory(self, input_dir: str, output_dir: Optional[str] = None, 
                         process_func: Callable = None, recursive: bool = False,
                         overwrite: bool = False, **kwargs) -> List[bool]:
        """
        Process all supported files in a directory
        
        Args:
            input_dir: Input directory path
            output_dir: Output directory path (optional)
            process_func: Function to process each file
            recursive: Whether to process subdirectories
            overwrite: Whether to overwrite existing files
            **kwargs: Additional arguments for process_func
        
        Returns:
            List of processing results (True/False for each file)
        """
        input_path = Path(input_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        if not input_path.is_dir():
            raise NotADirectoryError(f"Input path is not a directory: {input_dir}")
        
        # Find all supported files
        files = self.find_files(input_path, recursive)
        
        if not files:
            print(f"No supported files found in {input_dir}")
            return []
        
        # Create output directory if needed
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = input_path
        
        results = []
        
        # Process files with progress bar
        for file_path in tqdm(files, desc=self.progress_desc):
            try:
                # Generate output path
                if output_dir:
                    # Preserve directory structure if recursive
                    if recursive:
                        relative_path = file_path.relative_to(input_path)
                        output_file = output_path / relative_path
                        output_file.parent.mkdir(parents=True, exist_ok=True)
                    else:
                        output_file = output_path / file_path.name
                else:
                    output_file = file_path
                
                # Check if output file exists
                if output_file.exists() and not overwrite:
                    print(f"Skipping {file_path.name} (output exists)")
                    results.append(False)
                    continue
                
                # Process file
                if process_func:
                    result = process_func(str(file_path), str(output_file), **kwargs)
                    results.append(result)
                else:
                    results.append(True)
                    
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")
                results.append(False)
        
        return results
    
    def process_single_file(self, input_file: str, output_file: Optional[str] = None,
                           process_func: Callable = None, **kwargs) -> bool:
        """
        Process a single file
        
        Args:
            input_file: Input file path
            output_file: Output file path (optional)
            process_func: Function to process the file
            **kwargs: Additional arguments for process_func
        
        Returns:
            bool: True if successful, False otherwise
        """
        input_path = Path(input_file)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        if not self.is_supported_file(input_path):
            raise ValueError(f"Unsupported file format: {input_path.suffix}")
        
        # Generate output path if not provided
        if output_file is None:
            output_file = str(input_path.parent / f"{input_path.stem}_processed{input_path.suffix}")
        
        try:
            # Ensure output directory exists
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Process file
            if process_func:
                return process_func(str(input_path), str(output_path), **kwargs)
            else:
                return True
                
        except Exception as e:
            print(f"Error processing {input_file}: {e}")
            return False


class ImageProcessor(FileProcessor):
    """Processor for image files"""
    
    def __init__(self):
        super().__init__(
            supported_extensions=['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'],
            progress_desc="Processing images"
        )


class VideoProcessor(FileProcessor):
    """Processor for video files"""
    
    def __init__(self):
        super().__init__(
            supported_extensions=['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'],
            progress_desc="Processing videos"
        )


class AudioProcessor(FileProcessor):
    """Processor for audio files"""
    
    def __init__(self):
        super().__init__(
            supported_extensions=['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a'],
            progress_desc="Processing audio files"
        )


class DirectoryManager:
    """Directory management utilities"""
    
    @staticmethod
    def create_output_directory(input_path: str, output_dir: Optional[str] = None, 
                              suffix: str = "_output") -> Path:
        """
        Create output directory based on input path
        
        Args:
            input_path: Input file or directory path
            output_dir: Explicit output directory (optional)
            suffix: Suffix to add to directory name
        
        Returns:
            Path: Created output directory path
        """
        input_path = Path(input_path)
        
        if output_dir:
            output_path = Path(output_dir)
        else:
            if input_path.is_file():
                output_path = input_path.parent / f"{input_path.stem}{suffix}"
            else:
                output_path = input_path.parent / f"{input_path.name}{suffix}"
        
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path
    
    @staticmethod
    def create_temp_directory(prefix: str = "pyxelart_temp") -> Path:
        """Create temporary directory"""
        import tempfile
        temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
        return temp_dir
    
    @staticmethod
    def cleanup_directory(directory: Path, keep_files: List[str] = None) -> bool:
        """
        Clean up directory, optionally keeping specific files
        
        Args:
            directory: Directory to clean
            keep_files: List of files to keep (optional)
        
        Returns:
            bool: True if successful
        """
        try:
            if not directory.exists():
                return True
            
            if keep_files:
                keep_files = [Path(f).name for f in keep_files]
            
            for item in directory.iterdir():
                if keep_files and item.name in keep_files:
                    continue
                
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            
            return True
            
        except Exception as e:
            print(f"Error cleaning directory {directory}: {e}")
            return False
    
    @staticmethod
    def safe_remove_directory(directory: Path) -> bool:
        """Safely remove directory"""
        try:
            if directory.exists():
                shutil.rmtree(directory)
            return True
        except Exception as e:
            print(f"Error removing directory {directory}: {e}")
            return False
    
    @staticmethod
    def get_directory_size(directory: Path) -> int:
        """Get total size of directory in bytes"""
        total_size = 0
        for item in directory.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
        return total_size
    
    @staticmethod
    def copy_directory_structure(source: Path, destination: Path) -> bool:
        """Copy directory structure without files"""
        try:
            for item in source.rglob('*'):
                if item.is_dir():
                    relative_path = item.relative_to(source)
                    dest_dir = destination / relative_path
                    dest_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error copying directory structure: {e}")
            return False


class FileValidator:
    """File validation utilities"""
    
    @staticmethod
    def validate_input_file(file_path: str, supported_extensions: List[str]) -> bool:
        """
        Validate input file
        
        Args:
            file_path: Path to validate
            supported_extensions: List of supported extensions
        
        Returns:
            bool: True if valid
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        if path.suffix.lower() not in supported_extensions:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        
        return True
    
    @staticmethod
    def validate_input_directory(directory_path: str) -> bool:
        """
        Validate input directory
        
        Args:
            directory_path: Directory path to validate
        
        Returns:
            bool: True if valid
        """
        path = Path(directory_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory_path}")
        
        return True
    
    @staticmethod
    def validate_output_path(output_path: str, create_parents: bool = True) -> bool:
        """
        Validate output path
        
        Args:
            output_path: Output path to validate
            create_parents: Whether to create parent directories
        
        Returns:
            bool: True if valid
        """
        path = Path(output_path)
        
        # Check if parent directory exists or can be created
        if create_parents:
            path.parent.mkdir(parents=True, exist_ok=True)
        elif not path.parent.exists():
            raise FileNotFoundError(f"Output directory not found: {path.parent}")
        
        return True


class BatchProcessor:
    """Batch processing utilities"""
    
    def __init__(self, processor: FileProcessor):
        self.processor = processor
    
    def process_batch(self, input_items: List[str], output_dir: Optional[str] = None,
                     process_func: Callable = None, max_workers: int = 1, **kwargs) -> List[bool]:
        """
        Process a batch of files
        
        Args:
            input_items: List of input file paths
            output_dir: Output directory (optional)
            process_func: Function to process each file
            max_workers: Number of parallel workers
            **kwargs: Additional arguments for process_func
        
        Returns:
            List of processing results
        """
        if max_workers == 1:
            # Sequential processing
            return self._process_sequential(input_items, output_dir, process_func, **kwargs)
        else:
            # Parallel processing
            return self._process_parallel(input_items, output_dir, process_func, max_workers, **kwargs)
    
    def _process_sequential(self, input_items: List[str], output_dir: Optional[str],
                           process_func: Callable, **kwargs) -> List[bool]:
        """Process files sequentially"""
        results = []
        
        for input_file in tqdm(input_items, desc=self.processor.progress_desc):
            try:
                # Generate output path
                if output_dir:
                    input_path = Path(input_file)
                    output_file = Path(output_dir) / input_path.name
                else:
                    output_file = None
                
                # Process file
                result = self.processor.process_single_file(
                    input_file, str(output_file) if output_file else None,
                    process_func, **kwargs
                )
                results.append(result)
                
            except Exception as e:
                print(f"Error processing {input_file}: {e}")
                results.append(False)
        
        return results
    
    def _process_parallel(self, input_items: List[str], output_dir: Optional[str],
                         process_func: Callable, max_workers: int, **kwargs) -> List[bool]:
        """Process files in parallel"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = [False] * len(input_items)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_index = {}
            for i, input_file in enumerate(input_items):
                # Generate output path
                if output_dir:
                    input_path = Path(input_file)
                    output_file = Path(output_dir) / input_path.name
                else:
                    output_file = None
                
                future = executor.submit(
                    self.processor.process_single_file,
                    input_file, str(output_file) if output_file else None,
                    process_func, **kwargs
                )
                future_to_index[future] = i
            
            # Process completed tasks
            for future in tqdm(as_completed(future_to_index), total=len(input_items), 
                             desc=self.processor.progress_desc):
                index = future_to_index[future]
                try:
                    result = future.result()
                    results[index] = result
                except Exception as e:
                    print(f"Error processing {input_items[index]}: {e}")
                    results[index] = False
        
        return results


# Convenience functions
def create_image_processor() -> ImageProcessor:
    """Create image processor instance"""
    return ImageProcessor()

def create_video_processor() -> VideoProcessor:
    """Create video processor instance"""
    return VideoProcessor()

def create_audio_processor() -> AudioProcessor:
    """Create audio processor instance"""
    return AudioProcessor()

def process_images_in_directory(directory: str, process_func: Callable, 
                              output_dir: Optional[str] = None, **kwargs) -> List[bool]:
    """Convenience function to process images in directory"""
    processor = ImageProcessor()
    return processor.process_directory(directory, output_dir, process_func, **kwargs)

def process_videos_in_directory(directory: str, process_func: Callable,
                              output_dir: Optional[str] = None, **kwargs) -> List[bool]:
    """Convenience function to process videos in directory"""
    processor = VideoProcessor()
    return processor.process_directory(directory, output_dir, process_func, **kwargs)