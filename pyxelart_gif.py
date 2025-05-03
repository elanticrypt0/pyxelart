#!/usr/bin/env python3
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import imageio
import argparse
import os
import tempfile
from pathlib import Path
from tqdm import tqdm

def apply_aspect_ratio(frame, target_ratio, method='resize'):
    """
    Aplica una relación de aspecto específica al frame
    
    Args:
        frame: El frame a procesar
        target_ratio: La relación de aspecto objetivo (ancho/alto), por ejemplo 4/3 o 1/1
        method: 'resize' para estirar la imagen, 'crop' para recortar
        
    Returns:
        El frame con la nueva relación de aspecto
    """
    h, w = frame.shape[:2]
    current_ratio = w / h
    
    if abs(current_ratio - target_ratio) < 0.01:
        # Ya tiene la relación de aspecto correcta
        return frame
    
    if method == 'resize':
        # Calcular nuevas dimensiones manteniendo la altura
        new_width = int(h * target_ratio)
        return cv2.resize(frame, (new_width, h), interpolation=cv2.INTER_LANCZOS4)
    
    elif method == 'crop':
        if current_ratio > target_ratio:
            # Imagen más ancha que lo deseado, recortar los lados
            new_w = int(h * target_ratio)
            # Centrar el recorte
            x_offset = (w - new_w) // 2
            return frame[:, x_offset:x_offset + new_w]
        else:
            # Imagen más alta que lo deseado, recortar arriba y abajo
            new_h = int(w / target_ratio)
            # Centrar el recorte
            y_offset = (h - new_h) // 2
            return frame[y_offset:y_offset + new_h, :]
    
    return frame

def parse_aspect_ratio(aspect_str):
    """Convierte una cadena de relación de aspecto a un valor numérico"""
    if aspect_str == "4:3":
        return 4/3
    elif aspect_str == "1:1":
        return 1.0
    elif aspect_str == "original":
        return None
    else:
        try:
            # Intentar interpretar como "x:y"
            parts = aspect_str.split(":")
            if len(parts) == 2:
                return float(parts[0]) / float(parts[1])
        except:
            pass
        
        raise ValueError(f"Formato de relación de aspecto no reconocido: {aspect_str}")

def apply_retro_effect(frame, color_depth=16, pixel_size=4, add_dialog=False, dialog_text=""):
    """Aplica el efecto retro a un frame individual"""
    # Convertir frame de OpenCV (BGR) a PIL (RGB)
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
    # Aplicar reducción de colores
    img = img.convert('P', palette=Image.ADAPTIVE, colors=color_depth)
    img = img.convert('RGB')
    
    # Pixelado
    pixel_width = img.width // pixel_size
    pixel_height = img.height // pixel_size
    img = img.resize((pixel_width, pixel_height), Image.NEAREST)
    img = img.resize((img.width * pixel_size, img.height * pixel_size), Image.NEAREST)
    
    # Opcional: añadir cuadro de diálogo estilo retro
    if add_dialog and dialog_text:
        dialog_height = pixel_size * 10
        canvas = Image.new('RGB', (img.width, img.height + dialog_height), (50, 50, 50))
        canvas.paste(img, (0, 0))
        
        draw = ImageDraw.Draw(canvas)
        dialog_box = (10, img.height + 5, img.width - 10, img.height + dialog_height - 5)
        draw.rectangle(dialog_box, fill=(80, 80, 80), outline=(200, 200, 200))
        
        try:
            font = ImageFont.truetype("arial.ttf", pixel_size * 3)
        except:
            font = ImageFont.load_default()
            
        text_pos = (dialog_box[0] + 10, dialog_box[1] + 10)
        draw.text(text_pos, dialog_text, fill=(0, 0, 200), font=font)
        
        img = canvas
    
    # Añadir ruido/dithering para estética retro
    np_img = np.array(img)
    noise = np.random.randint(0, 15, np_img.shape)
    np_img = np.clip(np_img + noise, 0, 255).astype(np.uint8)
    
    return np_img

def video_to_retro_gif(input_path, output_path=None, width=None, height=None, 
                     color_depth=16, pixel_size=4, frame_skip=1, fps=10, 
                     add_dialog=False, dialog_text="", aspect_ratio=None, aspect_method='resize'):
    """Convierte un video a GIF con efecto retro"""
    # Configuración de salida por defecto si no se especifica
    if not output_path:
        filename, _ = os.path.splitext(input_path)
        output_path = f"{filename}_retro-c{color_depth}-p{pixel_size}.gif"
    
    # Abrir el video
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise Exception(f"Error al abrir el video: {input_path}")
    
    # Obtener propiedades del video
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Usar dimensiones originales si no se especifican
    if not width:
        width = original_width
    if not height:
        height = original_height
    
    # Lista para almacenar frames procesados
    processed_frames = []
    
    # Directorio temporal para frames
    temp_dir = tempfile.mkdtemp()
    
    print(f"Procesando video ({total_frames} frames)...")
    print(f"  Origen: {os.path.basename(input_path)} ({original_width}x{original_height})")
    print(f"  Destino: {os.path.basename(output_path)} ({width}x{height} a {fps} FPS)")
    print(f"  Configuración: {color_depth} colores, pixelado {pixel_size}, salto de frames {frame_skip}")
    
    if aspect_ratio is not None:
        print(f"  Relación de aspecto: {aspect_ratio:.2f} (método: {aspect_method})")
    
    # Procesar frames
    frame_count = 0
    processed_count = 0
    
    with tqdm(total=total_frames//frame_skip) as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Saltar frames según frame_skip
            if frame_count % frame_skip == 0:
                # Aplicar relación de aspecto si se especifica
                if aspect_ratio is not None:
                    frame = apply_aspect_ratio(frame, aspect_ratio, aspect_method)
                
                # Redimensionar si se especifica
                if frame.shape[1] != width or frame.shape[0] != height:
                    frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LANCZOS4)
                
                # Aplicar efecto retro
                retro_frame = apply_retro_effect(
                    frame, color_depth, pixel_size, add_dialog, dialog_text
                )
                
                # Guardar frame en lista
                processed_frames.append(retro_frame)
                processed_count += 1
                pbar.update(1)
                
            frame_count += 1
    
    cap.release()
    
    print(f"Guardando GIF ({processed_count} frames)...")
    
    # Guardar como GIF
    imageio.mimsave(output_path, processed_frames, fps=fps)
    
    print(f"GIF retro guardado en: {output_path}")
    return output_path

def process_video_directory(input_dir, output_dir=None, width=None, height=None, 
                           color_depth=16, pixel_size=4, frame_skip=2, fps=10, 
                           add_dialog=False, dialog_text="", aspect_ratio=None, aspect_method='resize'):
    """
    Procesa todos los videos en un directorio convirtiéndolos a GIF
    """
    # Asegurar que el directorio existe
    input_path = Path(input_dir)
    if not input_path.exists() or not input_path.is_dir():
        raise ValueError(f"El directorio {input_dir} no existe")
    
    # Crear directorio de salida
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = input_path / "retro"
    
    output_path.mkdir(exist_ok=True)
    
    # Extensiones de videos a procesar
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    
    # Buscar todos los videos en el directorio
    videos = [f for f in input_path.iterdir() 
              if f.is_file() and f.suffix.lower() in video_extensions]
    
    if not videos:
        print(f"No se encontraron videos en {input_dir}")
        return
    
    print(f"Encontrados {len(videos)} videos para procesar")
    
    # Procesar cada video
    for i, file_path in enumerate(videos, 1):
        # Ruta de salida con el formato solicitado
        output_file = output_path / f"{file_path.stem}_retro-c{color_depth}-p{pixel_size}.gif"
        
        print(f"\nProcesando video {i}/{len(videos)}: {file_path.name}")
        
        # Procesar el video
        video_to_retro_gif(
            str(file_path), str(output_file), width, height, 
            color_depth, pixel_size, frame_skip, fps, 
            add_dialog, dialog_text, aspect_ratio, aspect_method
        )
    
    print(f"\nProceso completo: {len(videos)} videos convertidos a GIF")
    print(f"Resultados guardados en: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convertir videos a GIF con efecto retro')
    
    # Crear subparsers para los diferentes modos
    subparsers = parser.add_subparsers(dest='mode', help='Modo de operación')
    
    # Subparser para procesamiento individual
    parser_single = subparsers.add_parser('single', help='Procesar un solo video')
    parser_single.add_argument('input', help='Ruta del video de entrada')
    parser_single.add_argument('--output', help='Ruta para guardar el GIF')
    parser_single.add_argument('--width', type=int, help='Ancho de salida')
    parser_single.add_argument('--height', type=int, help='Alto de salida')
    parser_single.add_argument('--colors', type=int, default=16, help='Profundidad de color')
    parser_single.add_argument('--pixel-size', type=int, default=4, help='Tamaño de pixelado')
    parser_single.add_argument('--frame-skip', type=int, default=2, help='Saltar N frames entre cada captura')
    parser_single.add_argument('--fps', type=int, default=10, help='Frames por segundo del GIF')
    parser_single.add_argument('--dialog', action='store_true', help='Añadir cuadro de diálogo')
    parser_single.add_argument('--text', default='', help='Texto para el cuadro de diálogo')
    parser_single.add_argument('--aspect-ratio', choices=['4:3', '1:1', 'original'], default='original',
                               help='Relación de aspecto del GIF de salida')
    parser_single.add_argument('--aspect-method', choices=['resize', 'crop'], default='resize',
                               help='Método para ajustar la relación de aspecto')
    
    # Subparser para procesamiento por lotes
    parser_batch = subparsers.add_parser('batch', help='Procesar múltiples videos en un directorio')
    parser_batch.add_argument('input_dir', help='Directorio con los videos a procesar')
    parser_batch.add_argument('--output-dir', help='Directorio donde guardar los GIFs')
    parser_batch.add_argument('--width', type=int, help='Ancho de salida')
    parser_batch.add_argument('--height', type=int, help='Alto de salida')
    parser_batch.add_argument('--colors', type=int, default=16, help='Profundidad de color')
    parser_batch.add_argument('--pixel-size', type=int, default=4, help='Tamaño de pixelado')
    parser_batch.add_argument('--frame-skip', type=int, default=2, help='Saltar N frames entre cada captura')
    parser_batch.add_argument('--fps', type=int, default=10, help='Frames por segundo del GIF')
    parser_batch.add_argument('--dialog', action='store_true', help='Añadir cuadro de diálogo')
    parser_batch.add_argument('--text', default='', help='Texto para el cuadro de diálogo')
    parser_batch.add_argument('--aspect-ratio', choices=['4:3', '1:1', 'original'], default='original',
                             help='Relación de aspecto de los GIFs de salida')
    parser_batch.add_argument('--aspect-method', choices=['resize', 'crop'], default='resize',
                             help='Método para ajustar la relación de aspecto')
    
    args = parser.parse_args()
    
    try:
        # Convertir aspect_ratio a valor numérico
        aspect_ratio_value = None
        if hasattr(args, 'aspect_ratio'):
            aspect_ratio_value = parse_aspect_ratio(args.aspect_ratio)
        
        if args.mode == 'single':
            video_to_retro_gif(
                args.input, args.output, args.width, args.height, 
                args.colors, args.pixel_size, args.frame_skip, args.fps,
                args.dialog, args.text, aspect_ratio_value, args.aspect_method
            )
        elif args.mode == 'batch':
            process_video_directory(
                args.input_dir, args.output_dir, args.width, args.height,
                args.colors, args.pixel_size, args.frame_skip, args.fps,
                args.dialog, args.text, aspect_ratio_value, args.aspect_method
            )
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")