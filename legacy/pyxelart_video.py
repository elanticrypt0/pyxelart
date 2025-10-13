#!/usr/bin/env python3
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import argparse
import os
import tempfile
import subprocess
from pathlib import Path
from tqdm import tqdm

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
    
    # Convertir de RGB a BGR para OpenCV
    return cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)

def get_video_codec(output_format):
    """Devuelve el codec adecuado según el formato de salida"""
    format_codecs = {
        '.mp4': 'mp4v',
        '.avi': 'XVID',
        '.mov': 'mp4v',
        '.mkv': 'X264',
    }
    
    return format_codecs.get(output_format.lower(), 'mp4v')

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

def get_ffmpeg_codec(output_format):
    """Devuelve los parámetros de codec para FFmpeg según el formato de salida"""
    # Mapeo de extensiones a codecs para FFmpeg
    format_codecs = {
        '.mp4': 'libx264',
        '.avi': 'libxvid',
        '.mov': 'libx264',
        '.mkv': 'libx264',
    }
    
    return format_codecs.get(output_format.lower(), 'libx264')

def video_to_retro_video(input_path, output_path=None, width=None, height=None, 
                          color_depth=16, pixel_size=4, frame_skip=1, fps=None, 
                          add_dialog=False, dialog_text="", output_format='.mp4',
                          aspect_ratio=None, aspect_method='resize',
                          quality=23, preset='medium'):
    """Convierte un video a otro video con efecto retro conservando el audio"""
    # Verificar que FFmpeg está instalado
    if not check_ffmpeg():
        print("ADVERTENCIA: FFmpeg no está instalado o no se encuentra en el PATH.")
        print("El audio NO será preservado en el video de salida.")
        preserve_audio = False
    else:
        preserve_audio = True
    
    # Configuración de salida por defecto si no se especifica
    if not output_path:
        filename, _ = os.path.splitext(input_path)
        output_path = f"{filename}_retro-c{color_depth}-p{pixel_size}{output_format}"
    else:
        # Asegurar que el formato de salida sea el correcto
        _, ext = os.path.splitext(output_path)
        if not ext:
            output_path = f"{output_path}{output_format}"
    
    # Abrir el video
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise Exception(f"Error al abrir el video: {input_path}")
    
    # Obtener propiedades del video
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Usar dimensiones originales si no se especifican
    if width is None:
        width = original_width
    if height is None:
        height = original_height
    
    # Calcular dimensiones basadas en la relación de aspecto si se especifica
    if aspect_ratio is not None:
        # Si se especificaron width y height, ajustar width para mantener la relación de aspecto
        if width is not None and height is not None:
            width = int(height * aspect_ratio)
    
    # Usar fps original si no se especifica
    if not fps:
        fps = original_fps
    
    # Calcular dimensiones finales considerando el diálogo
    final_height = height
    if add_dialog:
        final_height += pixel_size * 10
    
    # Determinar el codec basado en el formato de salida
    _, output_ext = os.path.splitext(output_path)
    fourcc = cv2.VideoWriter_fourcc(*get_video_codec(output_ext))
    
    # Crear un archivo temporal para el video sin audio
    temp_dir = tempfile.mkdtemp()
    temp_video = os.path.join(temp_dir, f"temp_video{output_ext}")
    
    # Configurar el escritor de video
    out = cv2.VideoWriter(temp_video if preserve_audio else output_path, 
                          fourcc, fps, (width, final_height))
    
    if not out.isOpened():
        raise Exception(f"Error al crear el video de salida. Asegúrate de que el codec es compatible con tu sistema.")
    
    print(f"Procesando video ({total_frames} frames)...")
    print(f"  Origen: {os.path.basename(input_path)} ({original_width}x{original_height} a {original_fps:.2f} FPS)")
    print(f"  Destino: {os.path.basename(output_path)} ({width}x{final_height} a {fps:.2f} FPS)")
    print(f"  Configuración: {color_depth} colores, pixelado {pixel_size}, salto de frames {frame_skip}")
    
    if aspect_ratio is not None:
        print(f"  Relación de aspecto: {aspect_ratio:.2f} (método: {aspect_method})")
    
    if preserve_audio:
        print(f"  Audio: Se preservará el audio original")
        print(f"  Calidad de compresión: {quality} (menor es mejor), preset: {preset}")
    else:
        print("  Audio: No se preservará (FFmpeg no disponible)")
    
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
                
                # Escribir frame al video de salida
                out.write(retro_frame)
                processed_count += 1
                pbar.update(1)
                
            frame_count += 1
    
    # Liberar recursos
    cap.release()
    out.release()
    
    # Si FFmpeg está disponible, combinar video procesado con audio original
    if preserve_audio:
        print(f"Combinando video procesado con audio original...")
        
        # Obtener el codec apropiado para el formato
        ffmpeg_codec = get_ffmpeg_codec(output_ext)
        
        # Comando FFmpeg: usar el audio del original y comprimir el video con la calidad especificada
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-i', temp_video,
            '-i', input_path,
            '-c:v', ffmpeg_codec,       # Usar codec específico para el formato
            '-crf', str(quality),       # Factor de calidad constante (menor = mejor calidad)
            '-preset', preset,          # Preset de codificación (afecta velocidad de compresión y tamaño)
            '-c:a', 'aac',              # Codec de audio
            '-b:a', '128k',             # Bitrate de audio
            '-map', '0:v:0',            # Usar el video del primer input (temp_video)
            '-map', '1:a:0',            # Usar el audio del segundo input (original)
            '-shortest',                # Terminar cuando la pista más corta termine
            output_path
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, check=True, 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
            print(f"Video con audio combinado guardado en: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error al combinar video y audio: {e}")
            print(f"Guardando video sin audio en: {output_path}")
            # Si falla, usar el video sin audio
            import shutil
            shutil.copy(temp_video, output_path)
    
    # Limpiar archivos temporales
    try:
        if os.path.exists(temp_video):
            os.remove(temp_video)
        os.rmdir(temp_dir)
    except:
        pass
    
    print(f"Procesados {processed_count} frames de {total_frames} (ratio {frame_skip}:1)")
    return output_path

def process_video_directory(input_dir, output_dir=None, width=None, height=None, 
                           color_depth=16, pixel_size=4, frame_skip=1, fps=None, 
                           add_dialog=False, dialog_text="", output_format='.mp4',
                           aspect_ratio=None, aspect_method='resize',
                           quality=23, preset='medium'):
    """
    Procesa todos los videos en un directorio
    """
    # Asegurar que el directorio existe
    input_path = Path(input_dir)
    if not input_path.exists() or not input_path.is_dir():
        raise ValueError(f"El directorio {input_dir} no existe")
    
    # Crear directorio de salida
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = input_path.parent / "retro"
    
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
        output_file = output_path / f"{file_path.stem}_retro-c{color_depth}-p{pixel_size}{output_format}"
        
        print(f"\nProcesando video {i}/{len(videos)}: {file_path.name}")
        
        # Procesar el video
        video_to_retro_video(
            str(file_path), str(output_file), width, height, 
            color_depth, pixel_size, frame_skip, fps, 
            add_dialog, dialog_text, output_format,
            aspect_ratio, aspect_method, quality, preset
        )
    
    print(f"\nProceso completo: {len(videos)} videos convertidos")
    print(f"Resultados guardados en: {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convertir videos a formato retro')
    
    # Crear subparsers para los diferentes modos
    subparsers = parser.add_subparsers(dest='mode', help='Modo de operación')
    
    # Subparser para procesamiento individual
    parser_single = subparsers.add_parser('single', help='Procesar un solo video')
    parser_single.add_argument('input', help='Ruta del video de entrada')
    parser_single.add_argument('--output', help='Ruta para guardar el video procesado')
    parser_single.add_argument('--width', type=int, help='Ancho de salida')
    parser_single.add_argument('--height', type=int, help='Alto de salida')
    parser_single.add_argument('--colors', type=int, default=16, help='Profundidad de color')
    parser_single.add_argument('--pixel-size', type=int, default=4, help='Tamaño de pixelado')
    parser_single.add_argument('--frame-skip', type=int, default=1, help='Saltar N frames entre cada captura')
    parser_single.add_argument('--fps', type=int, help='Frames por segundo del video de salida')
    parser_single.add_argument('--dialog', action='store_true', help='Añadir cuadro de diálogo')
    parser_single.add_argument('--text', default='', help='Texto para el cuadro de diálogo')
    parser_single.add_argument('--format', default='.mp4', choices=['.mp4', '.avi', '.mov', '.mkv'], 
                               help='Formato del video de salida')
    parser_single.add_argument('--aspect-ratio', choices=['4:3', '1:1', 'original'], default='original',
                               help='Relación de aspecto del video de salida')
    parser_single.add_argument('--aspect-method', choices=['resize', 'crop'], default='resize',
                               help='Método para ajustar la relación de aspecto')
    parser_single.add_argument('--quality', type=int, default=23, help='Calidad de compresión (1-51, menor es mejor)')
    parser_single.add_argument('--preset', choices=['ultrafast', 'superfast', 'veryfast', 'faster', 
                                                   'fast', 'medium', 'slow', 'slower', 'veryslow'], 
                               default='medium', help='Preset de codificación (afecta velocidad/tamaño)')
    
    # Subparser para procesamiento por lotes
    parser_batch = subparsers.add_parser('batch', help='Procesar múltiples videos en un directorio')
    parser_batch.add_argument('input_dir', help='Directorio con los videos a procesar')
    parser_batch.add_argument('--output-dir', help='Directorio donde guardar los videos procesados')
    parser_batch.add_argument('--width', type=int, help='Ancho de salida')
    parser_batch.add_argument('--height', type=int, help='Alto de salida')
    parser_batch.add_argument('--colors', type=int, default=16, help='Profundidad de color')
    parser_batch.add_argument('--pixel-size', type=int, default=4, help='Tamaño de pixelado')
    parser_batch.add_argument('--frame-skip', type=int, default=1, help='Saltar N frames entre cada captura')
    parser_batch.add_argument('--fps', type=int, help='Frames por segundo del video de salida')
    parser_batch.add_argument('--dialog', action='store_true', help='Añadir cuadro de diálogo')
    parser_batch.add_argument('--text', default='', help='Texto para el cuadro de diálogo')
    parser_batch.add_argument('--format', default='.mp4', choices=['.mp4', '.avi', '.mov', '.mkv'], 
                             help='Formato de los videos de salida')
    parser_batch.add_argument('--aspect-ratio', choices=['4:3', '1:1', 'original'], default='original',
                             help='Relación de aspecto de los videos de salida')
    parser_batch.add_argument('--aspect-method', choices=['resize', 'crop'], default='resize',
                             help='Método para ajustar la relación de aspecto')
    parser_batch.add_argument('--quality', type=int, default=23, help='Calidad de compresión (1-51, menor es mejor)')
    parser_batch.add_argument('--preset', choices=['ultrafast', 'superfast', 'veryfast', 'faster', 
                                                 'fast', 'medium', 'slow', 'slower', 'veryslow'], 
                             default='medium', help='Preset de codificación (afecta velocidad/tamaño)')
    
    args = parser.parse_args()
    
    try:
        # Convertir aspect_ratio a valor numérico
        aspect_ratio_value = None
        if hasattr(args, 'aspect_ratio'):
            aspect_ratio_value = parse_aspect_ratio(args.aspect_ratio)
        
        if args.mode == 'single':
            video_to_retro_video(
                args.input, args.output, args.width, args.height, 
                args.colors, args.pixel_size, args.frame_skip, args.fps,
                args.dialog, args.text, args.format,
                aspect_ratio_value, args.aspect_method,
                args.quality, args.preset
            )
        elif args.mode == 'batch':
            process_video_directory(
                args.input_dir, args.output_dir, args.width, args.height,
                args.colors, args.pixel_size, args.frame_skip, args.fps,
                args.dialog, args.text, args.format,
                aspect_ratio_value, args.aspect_method,
                args.quality, args.preset
            )
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")