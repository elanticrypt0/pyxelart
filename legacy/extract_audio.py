#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from pathlib import Path
from tqdm import tqdm

def check_ffmpeg():
    """Verifica si FFmpeg está instalado en el sistema"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def get_audio_info(video_path):
    """Obtiene información del audio del video"""
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'a:0',
            '-show_entries', 'stream=codec_name,channels,sample_rate,bit_rate',
            '-of', 'default=noprint_wrappers=1',
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            info = {}
            for line in result.stdout.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    info[key] = value
            return info
        return None
    except:
        return None

def extract_audio(input_video, output_path=None, format='mp3', quality='192k', 
                 sample_rate=None, channels=None, codec=None):
    """
    Extrae audio de un archivo de video
    
    Args:
        input_video: Ruta del video de entrada
        output_path: Ruta del archivo de audio de salida
        format: Formato de salida (mp3, wav, aac, flac, ogg)
        quality: Calidad/bitrate del audio (128k, 192k, 256k, 320k para mp3)
        sample_rate: Frecuencia de muestreo (44100, 48000, etc.)
        channels: Número de canales (1=mono, 2=stereo)
        codec: Codec específico a usar
    """
    if not check_ffmpeg():
        raise RuntimeError("FFmpeg no está instalado. Por favor instala FFmpeg para continuar.")
    
    # Verificar que el archivo de entrada existe
    if not os.path.exists(input_video):
        raise FileNotFoundError(f"El archivo de video no existe: {input_video}")
    
    # Determinar la ruta de salida
    if not output_path:
        base_name = Path(input_video).stem
        output_path = f"{base_name}_audio.{format}"
    else:
        # Asegurar que la extensión coincida con el formato
        output_path = str(Path(output_path).with_suffix(f".{format}"))
    
    # Obtener información del audio original
    audio_info = get_audio_info(input_video)
    if audio_info:
        print(f"Información del audio original:")
        print(f"  Codec: {audio_info.get('codec_name', 'desconocido')}")
        print(f"  Canales: {audio_info.get('channels', 'desconocido')}")
        print(f"  Frecuencia: {audio_info.get('sample_rate', 'desconocido')} Hz")
        print(f"  Bitrate: {audio_info.get('bit_rate', 'desconocido')} bps")
        print()
    
    # Construir el comando FFmpeg
    cmd = ['ffmpeg', '-i', input_video, '-vn']  # -vn = no video
    
    # Configurar el formato y codec
    format_configs = {
        'mp3': {
            'codec': 'libmp3lame',
            'quality_param': '-b:a',
            'default_quality': '192k'
        },
        'aac': {
            'codec': 'aac',
            'quality_param': '-b:a',
            'default_quality': '192k'
        },
        'wav': {
            'codec': 'pcm_s16le',
            'quality_param': None,
            'default_quality': None
        },
        'flac': {
            'codec': 'flac',
            'quality_param': '-compression_level',
            'default_quality': '8'
        },
        'ogg': {
            'codec': 'libvorbis',
            'quality_param': '-q:a',
            'default_quality': '6'
        }
    }
    
    # Aplicar configuración del formato
    if format in format_configs:
        config = format_configs[format]
        
        # Codec
        if codec:
            cmd.extend(['-acodec', codec])
        else:
            cmd.extend(['-acodec', config['codec']])
        
        # Calidad
        if config['quality_param'] and quality:
            if format == 'ogg' and quality.endswith('k'):
                # Convertir bitrate a escala de calidad para OGG (0-10)
                bitrate = int(quality[:-1])
                ogg_quality = min(10, max(0, bitrate // 32))
                cmd.extend([config['quality_param'], str(ogg_quality)])
            else:
                cmd.extend([config['quality_param'], quality])
    else:
        # Formato personalizado
        if codec:
            cmd.extend(['-acodec', codec])
        if quality:
            cmd.extend(['-b:a', quality])
    
    # Frecuencia de muestreo
    if sample_rate:
        cmd.extend(['-ar', str(sample_rate)])
    
    # Canales
    if channels:
        cmd.extend(['-ac', str(channels)])
    
    # Archivo de salida
    cmd.extend(['-y', output_path])  # -y = sobrescribir si existe
    
    # Mostrar el comando que se ejecutará
    print(f"Ejecutando: {' '.join(cmd)}")
    print()
    
    # Ejecutar el comando con barra de progreso
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    # Monitorear el progreso
    duration = None
    with tqdm(total=100, desc="Extrayendo audio", unit="%") as pbar:
        for line in process.stderr:
            # Buscar la duración total
            if "Duration:" in line and not duration:
                try:
                    time_str = line.split("Duration:")[1].split(",")[0].strip()
                    hours, minutes, seconds = time_str.split(":")
                    duration = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                except:
                    pass
            
            # Buscar el tiempo actual
            if "time=" in line and duration:
                try:
                    time_str = line.split("time=")[1].split()[0]
                    hours, minutes, seconds = time_str.split(":")
                    current_time = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                    progress = (current_time / duration) * 100
                    pbar.n = progress
                    pbar.refresh()
                except:
                    pass
    
    process.wait()
    
    if process.returncode == 0:
        print(f"\nAudio extraído exitosamente: {output_path}")
        
        # Mostrar información del archivo de salida
        output_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        print(f"Tamaño del archivo: {output_size:.2f} MB")
        
        # Obtener información del audio extraído
        output_info = get_audio_info(output_path)
        if output_info:
            print(f"Información del audio extraído:")
            print(f"  Formato: {format}")
            print(f"  Codec: {output_info.get('codec_name', 'desconocido')}")
            print(f"  Canales: {output_info.get('channels', 'desconocido')}")
            print(f"  Frecuencia: {output_info.get('sample_rate', 'desconocido')} Hz")
            print(f"  Bitrate: {output_info.get('bit_rate', 'desconocido')} bps")
    else:
        error_output = process.stderr.read()
        raise RuntimeError(f"Error al extraer audio: {error_output}")
    
    return output_path

def process_video_directory(input_dir, output_dir=None, format='mp3', quality='192k',
                          sample_rate=None, channels=None, codec=None):
    """
    Procesa todos los videos en un directorio
    """
    input_path = Path(input_dir)
    if not input_path.exists() or not input_path.is_dir():
        raise ValueError(f"El directorio {input_dir} no existe")
    
    # Crear directorio de salida
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = input_path / "audio"
    
    output_path.mkdir(exist_ok=True)
    
    # Extensiones de video soportadas
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']
    
    # Buscar todos los videos
    videos = [f for f in input_path.iterdir() 
              if f.is_file() and f.suffix.lower() in video_extensions]
    
    if not videos:
        print(f"No se encontraron videos en {input_dir}")
        return
    
    print(f"Encontrados {len(videos)} videos para procesar")
    
    # Procesar cada video
    successful = 0
    failed = 0
    
    for i, video_file in enumerate(videos, 1):
        print(f"\nProcesando video {i}/{len(videos)}: {video_file.name}")
        
        output_file = output_path / f"{video_file.stem}.{format}"
        
        try:
            extract_audio(
                str(video_file),
                str(output_file),
                format=format,
                quality=quality,
                sample_rate=sample_rate,
                channels=channels,
                codec=codec
            )
            successful += 1
        except Exception as e:
            print(f"Error procesando {video_file.name}: {e}")
            failed += 1
    
    print(f"\nProceso completo:")
    print(f"  Exitosos: {successful}")
    print(f"  Fallidos: {failed}")
    print(f"Archivos de audio guardados en: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Extraer audio de archivos de video')
    
    # Crear subparsers para diferentes modos
    subparsers = parser.add_subparsers(dest='mode', help='Modo de operación')
    
    # Subparser para archivo individual
    parser_single = subparsers.add_parser('single', help='Extraer audio de un solo video')
    parser_single.add_argument('input', help='Archivo de video de entrada')
    parser_single.add_argument('--output', help='Archivo de audio de salida')
    parser_single.add_argument('--format', choices=['mp3', 'wav', 'aac', 'flac', 'ogg'],
                              default='mp3', help='Formato de audio de salida')
    parser_single.add_argument('--quality', default='192k',
                              help='Calidad/bitrate del audio (ej: 128k, 192k, 256k, 320k)')
    parser_single.add_argument('--sample-rate', type=int,
                              help='Frecuencia de muestreo (ej: 44100, 48000)')
    parser_single.add_argument('--channels', type=int, choices=[1, 2],
                              help='Número de canales (1=mono, 2=stereo)')
    parser_single.add_argument('--codec', help='Codec específico a usar')
    
    # Subparser para procesamiento por lotes
    parser_batch = subparsers.add_parser('batch', help='Extraer audio de múltiples videos')
    parser_batch.add_argument('input_dir', help='Directorio con los videos')
    parser_batch.add_argument('--output-dir', help='Directorio de salida para los archivos de audio')
    parser_batch.add_argument('--format', choices=['mp3', 'wav', 'aac', 'flac', 'ogg'],
                             default='mp3', help='Formato de audio de salida')
    parser_batch.add_argument('--quality', default='192k',
                             help='Calidad/bitrate del audio (ej: 128k, 192k, 256k, 320k)')
    parser_batch.add_argument('--sample-rate', type=int,
                             help='Frecuencia de muestreo (ej: 44100, 48000)')
    parser_batch.add_argument('--channels', type=int, choices=[1, 2],
                             help='Número de canales (1=mono, 2=stereo)')
    parser_batch.add_argument('--codec', help='Codec específico a usar')
    
    args = parser.parse_args()
    
    if not args.mode:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.mode == 'single':
            extract_audio(
                args.input,
                args.output,
                format=args.format,
                quality=args.quality,
                sample_rate=args.sample_rate,
                channels=args.channels,
                codec=args.codec
            )
        elif args.mode == 'batch':
            process_video_directory(
                args.input_dir,
                args.output_dir,
                format=args.format,
                quality=args.quality,
                sample_rate=args.sample_rate,
                channels=args.channels,
                codec=args.codec
            )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()