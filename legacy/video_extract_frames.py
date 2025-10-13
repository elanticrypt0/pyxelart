#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import cv2
from PIL import Image
import numpy as np
from tqdm import tqdm

def extract_frames_from_video(video_path, output_dir, fps=None, preserve_alpha=True, 
                             output_format='webp', quality=80):
    """
    Extrae frames de un archivo de video
    
    Args:
        video_path: Ruta del video
        output_dir: Directorio de salida
        fps: FPS deseados (None = todos los frames)
        preserve_alpha: Intentar preservar canal alpha si existe
        output_format: Formato de salida ('png' o 'webp')
        quality: Calidad de compresión (1-100, solo para webp)
    """
    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)
    
    # Abrir el video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"No se pudo abrir el video: {video_path}")
    
    # Obtener información del video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"Video: {os.path.basename(video_path)}")
    print(f"FPS original: {video_fps}")
    print(f"Total frames: {total_frames}")
    
    # Calcular intervalo de frames si se especifica FPS
    frame_interval = 1
    if fps and fps < video_fps:
        frame_interval = int(video_fps / fps)
        print(f"Extrayendo a {fps} FPS (cada {frame_interval} frames)")
    
    frame_count = 0
    saved_count = 0
    
    # Iterar sobre todos los frames
    with tqdm(total=total_frames, desc="Extrayendo frames") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                # Convertir de BGR a RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Guardar el frame
                frame_filename = f"frame_{saved_count:04d}.{output_format}"
                frame_path = os.path.join(output_dir, frame_filename)
                
                # Guardar con el formato especificado
                if output_format == 'webp':
                    Image.fromarray(frame_rgb).save(frame_path, 'WEBP', quality=quality, lossless=False)
                else:  # png
                    Image.fromarray(frame_rgb).save(frame_path, 'PNG', optimize=True)
                saved_count += 1
            
            frame_count += 1
            pbar.update(1)
    
    cap.release()
    print(f"Extraídos {saved_count} frames")
    return saved_count

def extract_frames_from_gif(gif_path, output_dir, preserve_alpha=True, 
                           output_format='webp', quality=80):
    """
    Extrae frames de un archivo GIF preservando transparencia
    
    Args:
        gif_path: Ruta del GIF
        output_dir: Directorio de salida
        preserve_alpha: Preservar transparencia
        output_format: Formato de salida ('png' o 'webp')
        quality: Calidad de compresión (1-100, solo para webp)
    """
    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)
    
    # Abrir el GIF
    gif = Image.open(gif_path)
    
    # Verificar si es animado
    try:
        n_frames = gif.n_frames
    except:
        n_frames = 1
    
    print(f"GIF: {os.path.basename(gif_path)}")
    print(f"Frames: {n_frames}")
    
    # Obtener el tamaño del GIF
    width, height = gif.size
    
    # Crear un canvas base para componer los frames
    # Esto es necesario porque los GIFs pueden usar optimización de frames
    base_canvas = None
    
    # Extraer frames
    for i in tqdm(range(n_frames), desc="Extrayendo frames"):
        gif.seek(i)
        
        # Convertir el frame actual
        frame = gif.convert('RGBA')
        
        # Si es el primer frame o si el GIF usa disposal method 2 (restore to background)
        # necesitamos crear un nuevo canvas
        disposal_method = gif.disposal_method if hasattr(gif, 'disposal_method') else 0
        
        if i == 0 or disposal_method == 2:
            # Crear nuevo canvas transparente
            base_canvas = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        # Si el GIF usa disposal method 1 (do not dispose), 
        # mantenemos el canvas anterior
        
        # Obtener la posición del frame actual (algunos GIFs tienen frames que no cubren todo el canvas)
        if hasattr(gif, 'tile') and len(gif.tile) > 0:
            # Obtener las coordenadas del frame
            tile = gif.tile[0]
            if len(tile) > 2 and isinstance(tile[1], tuple) and len(tile[1]) == 4:
                left, top, right, bottom = tile[1]
                position = (left, top)
            else:
                position = (0, 0)
        else:
            position = (0, 0)
        
        # Componer el frame actual sobre el canvas base
        if base_canvas:
            # Crear una copia del canvas para este frame
            current_frame = base_canvas.copy()
            
            # Pegar el frame actual en la posición correcta
            current_frame.paste(frame, position, frame if preserve_alpha else None)
            
            # Actualizar el canvas base para el próximo frame si es necesario
            if disposal_method == 1:  # Do not dispose
                base_canvas = current_frame.copy()
            
            frame_to_save = current_frame
        else:
            frame_to_save = frame
        
        # Guardar el frame
        frame_filename = f"frame_{i:04d}.{output_format}"
        frame_path = os.path.join(output_dir, frame_filename)
        
        # Guardar con el formato especificado
        if output_format == 'webp':
            if preserve_alpha and frame_to_save.mode == 'RGBA':
                frame_to_save.save(frame_path, 'WEBP', quality=quality, lossless=False, exact=True)
            else:
                # Convertir a RGB si no queremos transparencia
                frame_to_save = frame_to_save.convert('RGB')
                frame_to_save.save(frame_path, 'WEBP', quality=quality, lossless=False)
        else:  # png
            if preserve_alpha and frame_to_save.mode == 'RGBA':
                frame_to_save.save(frame_path, 'PNG', optimize=True)
            else:
                # Convertir a RGB si no queremos transparencia
                frame_to_save = frame_to_save.convert('RGB')
                frame_to_save.save(frame_path, 'PNG', optimize=True)
    
    print(f"Extraídos {n_frames} frames")
    return n_frames

def main():
    parser = argparse.ArgumentParser(description='Extraer frames de videos o GIFs')
    parser.add_argument('input', help='Archivo de entrada (video o GIF)')
    parser.add_argument('--output-dir', '-o', help='Directorio de salida')
    parser.add_argument('--fps', type=float, help='FPS deseados (solo para videos)')
    parser.add_argument('--no-alpha', action='store_true', help='No preservar transparencia')
    parser.add_argument('--format', choices=['png', 'webp'], default='webp', 
                        help='Formato de salida (default: webp)')
    parser.add_argument('--quality', type=int, default=80, 
                        help='Calidad de compresión para WebP (1-100, default: 80)')
    
    args = parser.parse_args()
    
    # Determinar directorio de salida
    if not args.output_dir:
        input_name = Path(args.input).stem
        args.output_dir = f"{input_name}_frames"
    
    # Determinar tipo de archivo
    ext = Path(args.input).suffix.lower()
    
    # Validar calidad
    if args.quality < 1 or args.quality > 100:
        print("Error: La calidad debe estar entre 1 y 100")
        return
    
    try:
        if ext == '.gif':
            extract_frames_from_gif(args.input, args.output_dir, not args.no_alpha, 
                                   args.format, args.quality)
        elif ext in ['.mp4', '.avi', '.mov', '.webm', '.mkv']:
            extract_frames_from_video(args.input, args.output_dir, args.fps, not args.no_alpha,
                                     args.format, args.quality)
        else:
            print(f"Formato no soportado: {ext}")
            print("Formatos soportados: .gif, .mp4, .avi, .mov, .webm, .mkv")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()