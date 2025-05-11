#!/usr/bin/env python3
import argparse
import os
import re
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


def snake_case_filename(filename):
    """Convierte un nombre de archivo a snake_case sin extensión"""
    name = Path(filename).stem
    # Reemplazar caracteres no alfanuméricos con guiones bajos
    name = re.sub(r'[^a-zA-Z0-9]', '_', name)
    # Convertir camelCase o PascalCase a snake_case
    name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    # Eliminar guiones bajos múltiples
    name = re.sub(r'_+', '_', name)
    # Eliminar guiones bajos al inicio o final
    name = name.strip('_')
    return name


def get_video_info(video_path):
    """Obtiene información del video usando ffprobe"""
    try:
        # Obtener dimensiones del video
        cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,duration',
            '-of', 'csv=p=0', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        width, height, duration = result.stdout.strip().split(',')

        # Verificar si tiene audio
        cmd_audio = [
            'ffprobe', '-v', 'error', '-select_streams', 'a',
            '-show_entries', 'stream=codec_type', '-of', 'csv=p=0',
            video_path
        ]
        has_audio = len(subprocess.run(cmd_audio, capture_output=True,
                                       text=True).stdout.strip()) > 0

        return {
            'width': int(width),
            'height': int(height),
            'duration': float(duration) if duration else None,
            'has_audio': has_audio
        }
    except subprocess.CalledProcessError as e:
        print(f"Error al obtener información del video: {e}")
        return None
    except ValueError as e:
        print(f"Error al procesar información del video: {e}")
        return None


def convert_to_webm(input_video, output_path=None, quality=30,
                    resize=None, crop=None, threads=None, verbose=False):
    """
    Convierte un video al formato WebM

    Args:
        input_video: Ruta del video de entrada
        output_path: Ruta del video de salida (por defecto: nombre_original.webm)
        quality: Calidad del video (0-100), donde 0 es la peor y 100 la mejor
        resize: Tuple (width, height) para redimensionar el video
        crop: Tuple (x, y, width, height) para recortar el video
        threads: Número de hilos para la codificación
        verbose: Mostrar información detallada

    Returns:
        bool: True si la conversión fue exitosa, False en caso contrario
    """
    try:
        # Verificar si el video existe
        if not os.path.exists(input_video):
            print(f"Error: El archivo '{input_video}' no existe")
            return False

        # Obtener información del video
        video_info = get_video_info(input_video)
        if not video_info:
            return False

        # Determinar ruta de salida
        if not output_path:
            directory = os.path.dirname(input_video)
            filename = f"{snake_case_filename(os.path.basename(input_video))}.webm"
            output_path = os.path.join(directory, filename)

        # Convertir calidad (0-100) a bitrate aproximado (kbps)
        # Calibración más agresiva para generar archivos más pequeños
        if quality < 30:
            # Calidades muy bajas: 100-500 kbps
            bitrate = 100 + (400 * quality / 30)
        elif quality < 70:
            # Calidades medias: 500-2000 kbps
            bitrate = 500 + (1500 * (quality - 30) / 40)
        else:
            # Calidades altas: 2000-6000 kbps
            bitrate = 2000 + (4000 * (quality - 70) / 30)

        bitrate = int(bitrate)

        # Construir comando ffmpeg con menos verbosidad
        cmd = ['ffmpeg', '-y']

        # Reducir verbosidad si no está en modo verbose
        if not verbose:
            cmd.extend(['-v', 'warning'])

        cmd.extend(['-i', input_video])

        # Aplicar filtros si es necesario
        filter_complex = []

        # Filtro de recorte
        if crop:
            x, y, w, h = crop
            filter_complex.append(f"crop={w}:{h}:{x}:{y}")

        # Filtro de redimensionamiento
        if resize:
            width, height = resize
            filter_complex.append(f"scale={width}:{height}:force_original_aspect_ratio=decrease")

        # Agregar filtros al comando
        if filter_complex:
            cmd.extend(['-vf', ','.join(filter_complex)])

        # Configuración de codificación
        cmd.extend([
            '-c:v', 'libvpx-vp9',  # Codec VP9
            '-b:v', f'{bitrate}k',  # Bitrate
            '-deadline', 'good',  # Balance entre velocidad y calidad
            '-cpu-used', '4',  # Mayor valor = más rápido, menor calidad
            '-pix_fmt', 'yuv420p'  # Formato de pixel estándar para evitar advertencias
        ])

        # Configurar número de hilos
        if threads:
            cmd.extend(['-threads', str(threads)])

        # Configuración de audio
        if video_info['has_audio']:
            cmd.extend([
                '-c:a', 'libopus',  # Codec Opus para audio
                '-b:a', '96k'  # Bitrate de audio reducido
            ])

        # Archivo de salida
        cmd.append(output_path)

        # Mensaje inicial
        print(f"Convirtiendo: {os.path.basename(input_video)}")
        if verbose:
            print(f"Comando: {' '.join(cmd)}")

        # Ejecutar comando
        process = subprocess.run(cmd,
                                 capture_output=not verbose,
                                 text=True)
        process.check_returncode()

        # Verificar tamaños para comparación
        input_size = os.path.getsize(input_video) / (1024 * 1024)  # MB
        output_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        ratio = (output_size / input_size) * 100 if input_size > 0 else 0

        # Mostrar información de tamaño
        print(f"✓ {os.path.basename(output_path)} - {output_size:.2f} MB ({ratio:.1f}% del original)")

        return True

    except subprocess.CalledProcessError as e:
        print(f"Error durante la conversión: {e}")
        if not verbose and e.stderr:
            print(f"Detalles: {e.stderr.strip()}")
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False


def process_directory(input_dir, output_dir=None, quality=30, resize=None,
                      crop=None, recursive=False, max_workers=1, verbose=False):
    """
    Procesa todos los videos en un directorio

    Args:
        input_dir: Directorio de entrada
        output_dir: Directorio de salida (por defecto: input_dir/webm)
        quality: Calidad del video (0-100)
        resize: Tuple (width, height) para redimensionar
        crop: Tuple (x, y, width, height) para recortar
        recursive: Buscar videos en subdirectorios
        max_workers: Número máximo de trabajos en paralelo (default: 1)
        verbose: Mostrar información detallada

    Returns:
        dict: Estadísticas del proceso
    """
    # Verificar directorio de entrada
    if not os.path.exists(input_dir):
        print(f"Error: El directorio '{input_dir}' no existe")
        return {'total': 0, 'exito': 0, 'error': 0}

    # Determinar directorio de salida
    if not output_dir:
        output_dir = os.path.join(input_dir, 'webm')

    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)

    # Extensiones de video soportadas
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm')

    # Encontrar todos los videos
    videos = []

    if recursive:
        # Buscar en subdirectorios
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith(video_extensions):
                    videos.append(os.path.join(root, file))
    else:
        # Buscar solo en el directorio principal
        videos = [os.path.join(input_dir, f) for f in os.listdir(input_dir)
                  if f.lower().endswith(video_extensions)]

    if not videos:
        print(f"No se encontraron videos en '{input_dir}'")
        return {'total': 0, 'exito': 0, 'error': 0}

    print(f"Encontrados {len(videos)} videos para procesar")

    # Función para procesar un video individual
    def process_video(video_path):
        rel_path = os.path.relpath(video_path, input_dir)
        output_subdir = os.path.dirname(rel_path)

        # Crear subdirectorio en la salida si es necesario
        full_output_dir = os.path.join(output_dir, output_subdir)
        os.makedirs(full_output_dir, exist_ok=True)

        output_file = os.path.join(
            full_output_dir,
            f"{snake_case_filename(os.path.basename(video_path))}.webm"
        )

        # Comprobar si el archivo ya existe y es más reciente que el original
        if os.path.exists(output_file):
            input_time = os.path.getmtime(video_path)
            output_time = os.path.getmtime(output_file)
            if output_time >= input_time:
                print(f"Omitiendo {os.path.basename(video_path)} - ya procesado")
                return True

        # Convertir video
        success = convert_to_webm(
            video_path,
            output_file,
            quality,
            resize,
            crop,
            threads=1,  # Un solo hilo por worker
            verbose=verbose
        )

        return success

    # Procesar videos secuencialmente o en paralelo
    results = []
    if max_workers <= 1:
        # Procesamiento secuencial
        for video in videos:
            results.append(process_video(video))
    else:
        # Procesamiento en paralelo (limitado)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_video, video) for video in videos]
            for future in futures:
                results.append(future.result())

    # Estadísticas
    stats = {
        'total': len(videos),
        'exito': sum(results),
        'error': len(videos) - sum(results)
    }

    print(f"\nProceso completado:")
    print(f"- Total procesados: {stats['total']}")
    print(f"- Conversiones exitosas: {stats['exito']}")
    print(f"- Errores: {stats['error']}")

    return stats


def main():
    parser = argparse.ArgumentParser(description='Convertir videos a formato WebM')
    subparsers = parser.add_subparsers(dest='mode', help='Modo de operación')

    # Subparser para modo archivo único
    file_parser = subparsers.add_parser('file', help='Convertir un archivo')
    file_parser.add_argument('input', help='Archivo de video de entrada')
    file_parser.add_argument('--output', help='Ruta de salida (opcional)')

    # Subparser para modo directorio
    dir_parser = subparsers.add_parser('dir', help='Convertir todos los videos en un directorio')
    dir_parser.add_argument('input_dir', help='Directorio de entrada')
    dir_parser.add_argument('--output-dir', help='Directorio de salida (opcional)')
    dir_parser.add_argument('--recursive', action='store_true',
                            help='Buscar videos en subdirectorios')
    dir_parser.add_argument('--workers', type=int, default=1,
                            help='Número máximo de trabajos en paralelo (default: 1)')

    # Argumentos comunes
    for p in [file_parser, dir_parser]:
        p.add_argument('--quality', type=int, default=30,
                       help='Calidad del video (0-100, default: 30)')
        p.add_argument('--resize', type=str,
                       help='Redimensionar video (formato: widthxheight)')
        p.add_argument('--crop', type=str,
                       help='Recortar video (formato: x:y:width:height)')
        p.add_argument('--verbose', '-v', action='store_true',
                       help='Mostrar información detallada')

    args = parser.parse_args()

    # Validar argumentos
    if args.mode not in ['file', 'dir']:
        parser.print_help()
        return

    # Mostrar banner
    print("╔═══════════════════════════════════════╗")
    print("║          WebM Converter v1.0          ║")
    print("╚═══════════════════════════════════════╝")

    # Procesar argumentos de redimensionado
    resize = None
    if hasattr(args, 'resize') and args.resize:
        try:
            width, height = map(int, args.resize.split('x'))
            resize = (width, height)
        except ValueError:
            print("Error: Formato de resize incorrecto. Usar widthxheight (ej: 640x480)")
            return

    # Procesar argumentos de recorte
    crop = None
    if hasattr(args, 'crop') and args.crop:
        try:
            x, y, width, height = map(int, args.crop.split(':'))
            crop = (x, y, width, height)
        except ValueError:
            print("Error: Formato de crop incorrecto. Usar x:y:width:height (ej: 10:10:640:480)")
            return

    # Validar calidad
    if args.quality < 0 or args.quality > 100:
        print("Error: La calidad debe estar entre 0 y 100")
        return

    # Ejecutar en modo archivo único
    if args.mode == 'file':
        if not os.path.exists(args.input):
            print(f"Error: El archivo '{args.input}' no existe")
            return

        convert_to_webm(
            args.input,
            args.output,
            args.quality,
            resize,
            crop,
            verbose=args.verbose
        )

    # Ejecutar en modo directorio
    elif args.mode == 'dir':
        if not os.path.exists(args.input_dir):
            print(f"Error: El directorio '{args.input_dir}' no existe")
            return

        process_directory(
            args.input_dir,
            args.output_dir,
            args.quality,
            resize,
            crop,
            args.recursive,
            args.workers,
            args.verbose
        )


if __name__ == "__main__":
    main()