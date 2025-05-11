# Extract Audio - Video Audio Extraction Script

A Python script for extracting audio tracks from video files with support for multiple audio formats and quality settings.

## Features

- Extract audio from various video formats
- Support for multiple audio formats (MP3, WAV, AAC, FLAC, OGG)
- Customizable audio quality and bitrate
- Sample rate and channel control
- Batch processing for multiple videos
- Progress tracking during extraction
- Audio information display
- FFmpeg-based for maximum compatibility

## Requirements

### Python Dependencies
```bash
pip install tqdm
```

### System Requirements
- Python 3.7+
- **FFmpeg** (required)
  - Windows: Download from https://ffmpeg.org/download.html
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg`

## Usage

The script has two main modes:

### 1. Single Video Audio Extraction

```bash
python extract_audio.py single <input_video> [options]
```

### 2. Batch Video Processing

```bash
python extract_audio.py batch <input_directory> [options]
```

## Command Line Arguments

### Common Options

```
--format FORMAT          Audio format: mp3, wav, aac, flac, ogg (default: mp3)
--quality QUALITY        Audio quality/bitrate (default: 192k)
--sample-rate RATE      Sample rate in Hz (e.g., 44100, 48000)
--channels N            Number of channels: 1 (mono) or 2 (stereo)
--codec CODEC           Specific audio codec to use
```

### Single Mode Specific

```
--output PATH           Custom output path (default: input_audio.format)
```

### Batch Mode Specific

```
--output-dir DIR        Output directory (default: input_dir/audio)
```

## Supported Formats

### Input Video Formats
- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- WebM (.webm)
- FLV (.flv)
- WMV (.wmv)

### Output Audio Formats

#### MP3
- Codec: libmp3lame
- Quality: 64k to 320k bitrate
- Best for: General use, compatibility

#### WAV
- Codec: PCM (uncompressed)
- Quality: Lossless
- Best for: Professional audio, editing

#### AAC
- Codec: AAC
- Quality: 64k to 320k bitrate
- Best for: Modern devices, streaming

#### FLAC
- Codec: FLAC
- Quality: Lossless compression
- Best for: Archival, high quality

#### OGG
- Codec: Vorbis
- Quality: Scale 0-10
- Best for: Open source projects

## Examples

### Basic Usage

```bash
# Extract audio as MP3 with default settings
python extract_audio.py single video.mp4

# Extract audio from all videos in a directory
python extract_audio.py batch ./videos/
```

### Quality Control

```bash
# High quality MP3
python extract_audio.py single video.mp4 --quality 320k

# CD quality WAV
python extract_audio.py single video.mp4 --format wav --sample-rate 44100

# Compressed FLAC for archival
python extract_audio.py single video.mp4 --format flac
```

### Format Specific Examples

```bash
# Extract as AAC for mobile devices
python extract_audio.py single video.mp4 --format aac --quality 256k

# Extract as OGG with high quality
python extract_audio.py single video.mp4 --format ogg --quality 8

# Extract as mono MP3 for podcasts
python extract_audio.py single interview.mp4 --channels 1 --quality 128k
```

### Batch Processing

```bash
# Extract audio from all videos as high quality MP3
python extract_audio.py batch ./videos/ --quality 256k

# Convert to WAV for editing
python extract_audio.py batch ./footage/ --format wav --output-dir ./audio_tracks/

# Create compressed versions for web
python extract_audio.py batch ./videos/ --format aac --quality 128k
```

### Custom Settings

```bash
# Specific sample rate and channels
python extract_audio.py single concert.mp4 --sample-rate 48000 --channels 2

# Use specific codec
python extract_audio.py single video.mp4 --codec libopus --format ogg

# Custom output path
python extract_audio.py single video.mp4 --output soundtrack.mp3
```

## Quality Guidelines

### MP3 Bitrates
- 64-96k: Speech, podcasts
- 128k: Acceptable music quality
- 192k: Good music quality (default)
- 256k: Very good music quality
- 320k: Maximum MP3 quality

### Sample Rates
- 22050 Hz: Speech, low quality
- 44100 Hz: CD quality (recommended)
- 48000 Hz: Professional audio
- 96000 Hz: High-resolution audio

## Output Information

The script displays detailed information about:
- Original audio properties
- Processing progress
- Output file details
- Extraction success/failure status

## Integration with Other Tools

Works well in a pipeline:

```bash
# 1. Extract audio from video
python extract_audio.py single gameplay.mp4 --format wav

# 2. Process video frames
python nobg_video.py gameplay.mp4

# 3. Apply retro effects
python pyxelart.py batch gameplay/frames_nobg/

# 4. Use extracted audio in game engine
# Import gameplay_audio.wav into your game project
```

## Performance Notes

- Extraction speed depends on:
  - Video file size
  - Output format (WAV is fastest)
  - Quality settings
  - System performance

- Memory usage is generally low
- CPU usage varies by codec

## Troubleshooting

### Common Issues:

1. **FFmpeg Not Found**
   ```
   Error: FFmpeg not installed
   ```
   Solution: Install FFmpeg and ensure it's in system PATH

2. **No Audio Stream**
   ```
   Error: No audio stream found
   ```
   Solution: Verify the video contains audio

3. **Permission Errors**
   ```
   Error: Permission denied
   ```
   Solution: Check write permissions for output directory

4. **Codec Not Supported**
   ```
   Error: Unknown encoder
   ```
   Solution: Update FFmpeg or use a different codec

## Best Practices

1. **For Game Development**:
   ```bash
   python extract_audio.py single cutscene.mp4 --format wav
   ```

2. **For Web Use**:
   ```bash
   python extract_audio.py single video.mp4 --format aac --quality 128k
   ```

3. **For Archival**:
   ```bash
   python extract_audio.py single master.mp4 --format flac
   ```

4. **For Editing**:
   ```bash
   python extract_audio.py single footage.mp4 --format wav --sample-rate 48000
   ```

## Notes

- Always verify FFmpeg installation before use
- Lossless formats (WAV, FLAC) produce larger files
- Some video files may have multiple audio tracks
- The script extracts the first audio stream by default

## License

MIT License - Feel free to use and modify as needed.