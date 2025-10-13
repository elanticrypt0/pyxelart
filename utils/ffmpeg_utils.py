#!/usr/bin/env python3
"""
FFmpeg utilities for PyxelArt
Centralized FFmpeg operations and checks
"""

import subprocess
import shutil
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


class FFmpegManager:
    """Manager for FFmpeg operations"""
    
    @staticmethod
    def is_available() -> bool:
        """Check if FFmpeg is available on the system"""
        return shutil.which('ffmpeg') is not None
    
    @staticmethod
    def get_version() -> Optional[str]:
        """Get FFmpeg version"""
        if not FFmpegManager.is_available():
            return None
        
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Extract version from first line
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.startswith('ffmpeg version'):
                        return line.split(' ')[2]
            return None
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return None
    
    @staticmethod
    def check_installation() -> Tuple[bool, str]:
        """
        Check FFmpeg installation and return status
        
        Returns:
            tuple: (is_available, message)
        """
        if FFmpegManager.is_available():
            version = FFmpegManager.get_version()
            if version:
                return True, f"FFmpeg {version} is available"
            else:
                return True, "FFmpeg is available (version unknown)"
        else:
            return False, "FFmpeg is not installed or not in PATH"
    
    @staticmethod
    def get_media_info(file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get media file information using ffprobe
        
        Args:
            file_path: Path to media file
        
        Returns:
            dict: Media information or None if error
        """
        if not FFmpegManager.is_available():
            return None
        
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return None
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, json.JSONDecodeError):
            return None
    
    @staticmethod
    def get_video_info(file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get video-specific information
        
        Args:
            file_path: Path to video file
        
        Returns:
            dict: Video information
        """
        media_info = FFmpegManager.get_media_info(file_path)
        if not media_info:
            return None
        
        video_info = {}
        
        # Extract format information
        if 'format' in media_info:
            format_info = media_info['format']
            video_info.update({
                'duration': float(format_info.get('duration', 0)),
                'size': int(format_info.get('size', 0)),
                'bitrate': int(format_info.get('bit_rate', 0)),
                'format_name': format_info.get('format_name', ''),
                'format_long_name': format_info.get('format_long_name', '')
            })
        
        # Extract video stream information
        if 'streams' in media_info:
            for stream in media_info['streams']:
                if stream.get('codec_type') == 'video':
                    video_info.update({
                        'width': int(stream.get('width', 0)),
                        'height': int(stream.get('height', 0)),
                        'fps': eval(stream.get('r_frame_rate', '0/1')),
                        'codec': stream.get('codec_name', ''),
                        'pixel_format': stream.get('pix_fmt', ''),
                        'video_bitrate': int(stream.get('bit_rate', 0))
                    })
                    break
        
        return video_info
    
    @staticmethod
    def get_audio_info(file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get audio-specific information
        
        Args:
            file_path: Path to audio/video file
        
        Returns:
            dict: Audio information
        """
        media_info = FFmpegManager.get_media_info(file_path)
        if not media_info:
            return None
        
        audio_info = {}
        
        # Extract audio stream information
        if 'streams' in media_info:
            for stream in media_info['streams']:
                if stream.get('codec_type') == 'audio':
                    audio_info.update({
                        'codec': stream.get('codec_name', ''),
                        'sample_rate': int(stream.get('sample_rate', 0)),
                        'channels': int(stream.get('channels', 0)),
                        'channel_layout': stream.get('channel_layout', ''),
                        'audio_bitrate': int(stream.get('bit_rate', 0)),
                        'duration': float(stream.get('duration', 0))
                    })
                    break
        
        return audio_info
    
    @staticmethod
    def extract_frames(video_path: str, output_dir: str, fps: Optional[float] = None,
                      format: str = 'png', quality: int = 95, start_time: float = 0,
                      duration: Optional[float] = None) -> bool:
        """
        Extract frames from video using FFmpeg
        
        Args:
            video_path: Input video path
            output_dir: Output directory for frames
            fps: Target FPS (None for original)
            format: Output format (png, jpg, webp)
            quality: Output quality for lossy formats
            start_time: Start time in seconds
            duration: Duration in seconds (None for full video)
        
        Returns:
            bool: True if successful
        """
        if not FFmpegManager.is_available():
            return False
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Build command
        cmd = ['ffmpeg', '-i', video_path]
        
        # Add start time if specified
        if start_time > 0:
            cmd.extend(['-ss', str(start_time)])
        
        # Add duration if specified
        if duration:
            cmd.extend(['-t', str(duration)])
        
        # Add FPS filter if specified
        if fps:
            cmd.extend(['-vf', f'fps={fps}'])
        
        # Add quality settings
        if format.lower() in ['jpg', 'jpeg']:
            cmd.extend(['-q:v', str(max(1, min(31, 31 - int(quality * 0.3))))])
        elif format.lower() == 'webp':
            cmd.extend(['-quality', str(quality)])
        
        # Output pattern
        output_pattern = os.path.join(output_dir, f'frame_%04d.{format}')
        cmd.append(output_pattern)
        
        # Add overwrite flag
        cmd.insert(1, '-y')
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
    
    @staticmethod
    def extract_audio(video_path: str, output_path: str, format: str = 'mp3',
                     bitrate: str = '192k', sample_rate: Optional[int] = None,
                     channels: Optional[int] = None) -> bool:
        """
        Extract audio from video using FFmpeg
        
        Args:
            video_path: Input video path
            output_path: Output audio path
            format: Audio format (mp3, wav, aac, flac, ogg)
            bitrate: Audio bitrate
            sample_rate: Sample rate (Hz)
            channels: Number of channels
        
        Returns:
            bool: True if successful
        """
        if not FFmpegManager.is_available():
            return False
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Build command
        cmd = ['ffmpeg', '-y', '-i', video_path]
        
        # Audio codec selection
        codec_map = {
            'mp3': 'libmp3lame',
            'wav': 'pcm_s16le',
            'aac': 'aac',
            'flac': 'flac',
            'ogg': 'libvorbis',
            'm4a': 'aac'
        }
        
        codec = codec_map.get(format.lower(), 'libmp3lame')
        cmd.extend(['-acodec', codec])
        
        # Quality settings
        if format.lower() in ['mp3', 'aac', 'm4a']:
            cmd.extend(['-b:a', bitrate])
        elif format.lower() == 'ogg':
            cmd.extend(['-q:a', '6'])
        elif format.lower() == 'flac':
            cmd.extend(['-compression_level', '8'])
        
        # Sample rate
        if sample_rate:
            cmd.extend(['-ar', str(sample_rate)])
        
        # Channels
        if channels:
            cmd.extend(['-ac', str(channels)])
        
        # Disable video
        cmd.extend(['-vn'])
        
        # Output file
        cmd.append(output_path)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
    
    @staticmethod
    def convert_video(input_path: str, output_path: str, codec: str = 'libx264',
                     quality: int = 23, preset: str = 'medium', fps: Optional[float] = None,
                     resolution: Optional[Tuple[int, int]] = None, audio_codec: str = 'aac',
                     audio_bitrate: str = '128k') -> bool:
        """
        Convert video format using FFmpeg
        
        Args:
            input_path: Input video path
            output_path: Output video path
            codec: Video codec
            quality: Video quality (CRF)
            preset: Encoding preset
            fps: Target FPS
            resolution: Target resolution (width, height)
            audio_codec: Audio codec
            audio_bitrate: Audio bitrate
        
        Returns:
            bool: True if successful
        """
        if not FFmpegManager.is_available():
            return False
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Build command
        cmd = ['ffmpeg', '-y', '-i', input_path]
        
        # Video codec and quality
        cmd.extend(['-c:v', codec, '-crf', str(quality), '-preset', preset])
        
        # Video filters
        filters = []
        
        if fps:
            filters.append(f'fps={fps}')
        
        if resolution:
            width, height = resolution
            filters.append(f'scale={width}:{height}')
        
        if filters:
            cmd.extend(['-vf', ','.join(filters)])
        
        # Audio codec and bitrate
        cmd.extend(['-c:a', audio_codec, '-b:a', audio_bitrate])
        
        # Output file
        cmd.append(output_path)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
    
    @staticmethod
    def create_video_from_frames(frames_dir: str, output_path: str, fps: float = 30,
                               codec: str = 'libx264', quality: int = 23,
                               preset: str = 'medium', pattern: str = 'frame_%04d.png') -> bool:
        """
        Create video from frame sequence
        
        Args:
            frames_dir: Directory containing frames
            output_path: Output video path
            fps: Output FPS
            codec: Video codec
            quality: Video quality (CRF)
            preset: Encoding preset
            pattern: Frame filename pattern
        
        Returns:
            bool: True if successful
        """
        if not FFmpegManager.is_available():
            return False
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Build command
        input_pattern = os.path.join(frames_dir, pattern)
        
        cmd = [
            'ffmpeg', '-y',
            '-framerate', str(fps),
            '-i', input_pattern,
            '-c:v', codec,
            '-crf', str(quality),
            '-preset', preset,
            '-pix_fmt', 'yuv420p',
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
    
    @staticmethod
    def get_codec_info() -> Dict[str, List[str]]:
        """Get available codecs"""
        if not FFmpegManager.is_available():
            return {}
        
        codecs = {'video': [], 'audio': []}
        
        try:
            # Get video codecs
            result = subprocess.run(['ffmpeg', '-encoders'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                in_video = False
                in_audio = False
                
                for line in lines:
                    if 'Video:' in line:
                        in_video = True
                        in_audio = False
                        continue
                    elif 'Audio:' in line:
                        in_video = False
                        in_audio = True
                        continue
                    elif line.strip() == '':
                        continue
                    
                    if in_video and line.startswith(' V'):
                        parts = line.split()
                        if len(parts) > 1:
                            codecs['video'].append(parts[1])
                    elif in_audio and line.startswith(' A'):
                        parts = line.split()
                        if len(parts) > 1:
                            codecs['audio'].append(parts[1])
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
        
        return codecs


# Convenience functions
def check_ffmpeg() -> bool:
    """Check if FFmpeg is available"""
    return FFmpegManager.is_available()

def get_video_duration(file_path: str) -> Optional[float]:
    """Get video duration in seconds"""
    info = FFmpegManager.get_video_info(file_path)
    return info.get('duration') if info else None

def get_video_fps(file_path: str) -> Optional[float]:
    """Get video FPS"""
    info = FFmpegManager.get_video_info(file_path)
    return info.get('fps') if info else None

def get_video_resolution(file_path: str) -> Optional[Tuple[int, int]]:
    """Get video resolution as (width, height)"""
    info = FFmpegManager.get_video_info(file_path)
    if info and 'width' in info and 'height' in info:
        return (info['width'], info['height'])
    return None