#!/usr/bin/env python3
import argparse
import os
import re
import shutil
from pathlib import Path

# Importar funciones de los scripts existentes
from extract_frames import extract_frames_from_video
from nobg import process_image_directory

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

def process_video(input_video, output_dir=None, fps=None, model="u2net_human_seg",
                 alpha_matting=False, alpha_matting_foreground_threshold=240,
                 alpha_matting_background_threshold=10, alpha_matting_erode_size=10,
                 quality=80, output_format='webp', keep_frames=False):
    """
    Procesa un video: extrae frames y remueve fondos
    
    Args:
        input_video: Ruta del video de entrada
        output_dir: Directorio de salida (por defecto: nombre_video_snake_case)
        fps: FPS para extraer frames (None = todos)
        model: Modelo para remover fondos
        alpha_matting: Usar alpha matting
        alpha_matting_foreground_threshold: Umbral para primer plano
        alpha_matting_background_threshold: Umbral para fondo
        alpha_matting_erode_size: Tamaño de erosión
        quality: Calidad de salida
        output_format: Formato de salida
        keep_frames: Mantener frames originales
    """
    # Determinar directorio de salida
    if not output_dir:
        output_dir = snake_case_filename(input_video)
    
    # Crear directorio principal
    os.makedirs(output_dir, exist_ok=True)
    
    # Directorios temporales
    frames_dir = os.path.join(output_dir, "frames_original")
    nobg_dir = os.path.join(output_dir, "frames_nobg")
    
    try:
        # Paso 1: Extraer frames usando extract_frames.py
        print(f"\n=== Paso 1/2: Extrayendo frames del video ===")
        extract_frames_from_video(
            video_path=input_video,
            output_dir=frames_dir,
            fps=fps,
            preserve_alpha=True,
            output_format=output_format,
            quality=quality
        )
        
        # Paso 2: Remover fondos usando nobg.py
        print(f"\n=== Paso 2/2: Removiendo fondos ===")
        process_image_directory(
            input_dir=frames_dir,
            output_dir=nobg_dir,
            model=model,
            alpha_matting=alpha_matting,
            alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
            alpha_matting_background_threshold=alpha_matting_background_threshold,
            alpha_matting_erode_size=alpha_matting_erode_size,
            quality=quality,
            output_format=output_format
        )
        
        # Limpiar frames originales si no se quieren mantener
        if not keep_frames:
            print("\nLimpiando frames originales...")
            shutil.rmtree(frames_dir)
        
        print(f"\n¡Proceso completado! Frames sin fondo guardados en: {nobg_dir}")
        
    except Exception as e:
        print(f"\nError durante el procesamiento: {e}")
        # Limpieza en caso de error
        if os.path.exists(frames_dir) and not keep_frames:
            shutil.rmtree(frames_dir, ignore_errors=True)
        raise

def main():
    parser = argparse.ArgumentParser(description='Remover fondo de videos frame por frame')
    parser.add_argument('input', help='Archivo de video de entrada')
    parser.add_argument('--output-dir', help='Directorio de salida (default: nombre_video_snake_case)')
    parser.add_argument('--fps', type=float, help='FPS para extraer frames (default: todos)')
    parser.add_argument('--model', choices=['u2net', 'u2netp', 'u2net_human_seg', 'silueta'],
                       default='u2net_human_seg', help='Modelo a utilizar')
    parser.add_argument('--alpha-matting', action='store_true',
                       help='Usar alpha matting para mejorar bordes')
    parser.add_argument('--foreground-threshold', type=int, default=240,
                       help='Umbral para primer plano en alpha matting (0-255)')
    parser.add_argument('--background-threshold', type=int, default=10,
                       help='Umbral para fondo en alpha matting (0-255)')
    parser.add_argument('--erode-size', type=int, default=10,
                       help='Tamaño de erosión para alpha matting')
    parser.add_argument('--quality', type=int, default=80,
                       help='Calidad de salida (1-100, default: 80)')
    parser.add_argument('--format', choices=['png', 'webp', 'tiff'],
                       default='webp', help='Formato de salida (default: webp)')
    parser.add_argument('--keep-frames', action='store_true',
                       help='Mantener frames originales')
    
    args = parser.parse_args()
    
    # Validar archivo de entrada
    if not os.path.exists(args.input):
        print(f"Error: El archivo '{args.input}' no existe")
        return
    
    # Validar formato de video
    video_extensions = ['.mp4', '.avi', '.mov', '.webm', '.mkv']
    if not any(args.input.lower().endswith(ext) for ext in video_extensions):
        print(f"Error: Formato de video no soportado. Usar: {', '.join(video_extensions)}")
        return
    
    # Validar calidad
    if args.quality < 1 or args.quality > 100:
        print("Error: La calidad debe estar entre 1 y 100")
        return
    
    try:
        process_video(
            args.input,
            args.output_dir,
            args.fps,
            args.model,
            args.alpha_matting,
            args.foreground_threshold,
            args.background_threshold,
            args.erode_size,
            args.quality,
            args.format,
            args.keep_frames
        )
    except ImportError as e:
        print(f"Error: No se pudieron importar los scripts necesarios.")
        print(f"Asegúrate de que 'extract_frames.py' y 'nobg.py' estén en el mismo directorio.")
        print(f"Detalles: {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()