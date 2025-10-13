#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops
import cv2
import argparse
import os
import tempfile
import subprocess
from pathlib import Path
from tqdm import tqdm

SUPPORTED_VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm')

# --- Funciones de Utilidad (similares a pyxelart_modificado_v2) ---
def apply_aspect_ratio_to_frame(cv2_frame, target_ratio, method='resize'):
    """
    Aplica una relación de aspecto específica al frame de OpenCV.
    """
    h, w = cv2_frame.shape[:2]
    current_ratio = w / h
    
    if abs(current_ratio - target_ratio) < 0.01:
        return cv2_frame
    
    if method == 'resize':
        new_width = int(h * target_ratio)
        if new_width == 0: new_width = 1
        return cv2.resize(cv2_frame, (new_width, h), interpolation=cv2.INTER_LANCZOS4)
    
    elif method == 'crop':
        if current_ratio > target_ratio:
            new_w = int(h * target_ratio)
            if new_w == 0: new_w = 1
            x_offset = (w - new_w) // 2
            return cv2_frame[:, x_offset:x_offset + new_w]
        else:
            new_h = int(w / target_ratio)
            if new_h == 0: new_h = 1
            y_offset = (h - new_h) // 2
            return cv2_frame[y_offset:y_offset + new_h, :]
    return cv2_frame

def parse_aspect_ratio_str(aspect_str):
    """Convierte una cadena de relación de aspecto a un valor numérico."""
    if aspect_str is None or aspect_str.lower() == "original":
        return None
    if aspect_str == "4:3":
        return 4/3
    elif aspect_str == "1:1":
        return 1.0
    else:
        try:
            parts = aspect_str.split(":")
            if len(parts) == 2:
                num = float(parts[0])
                den = float(parts[1])
                if den == 0: raise ValueError("El denominador de la relación de aspecto no puede ser cero.")
                return num / den
        except ValueError:
             raise ValueError(f"Formato de relación de aspecto no reconocido o inválido: {aspect_str}")
        raise ValueError(f"Formato de relación de aspecto no reconocido: {aspect_str}")

def apply_chromatic_aberration_on_pil_image(pil_image, intensity):
    """Aplica aberración cromática a una imagen PIL."""
    if intensity == 0:
        return pil_image
    img_copy = pil_image.copy()
    if img_copy.mode != 'RGBA':
        img_copy = img_copy.convert('RGBA')
    r, g, b, a = img_copy.split()
    offset = int(round(intensity))
    r_shifted = ImageChops.offset(r, -offset, 0)
    b_shifted = ImageChops.offset(b, offset, 0)
    return Image.merge('RGBA', (r_shifted, g, b_shifted, a))

# --- Procesamiento de Frames ---
def apply_effects_to_frame(cv2_frame, colors=16, pixel_size=4, 
                           add_dialog=False, dialog_text="",
                           chroma_intensity=0):
    """Aplica todos los efectos visuales a un frame individual (OpenCV BGR -> PIL -> OpenCV BGR)."""
    pil_img = Image.fromarray(cv2.cvtColor(cv2_frame, cv2.COLOR_BGR2RGB))
    
    # 1. Reducción de color y pixelado (Efecto Retro Principal)
    img_quantized = pil_img.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    img_quantized_rgb = img_quantized.convert('RGB') # Asegurar modo RGB después de cuantizar

    current_pixel_size = max(1, pixel_size) # Asegurar que pixel_size sea al menos 1
    pixel_width = max(1, img_quantized_rgb.width // current_pixel_size)
    pixel_height = max(1, img_quantized_rgb.height // current_pixel_size)
    
    img_pixelated = img_quantized_rgb.resize((pixel_width, pixel_height), Image.Resampling.NEAREST)
    img_pixelated = img_pixelated.resize((img_quantized_rgb.width, img_quantized_rgb.height), Image.Resampling.NEAREST)
    
    # 2. Ruido (Dithering Sutil)
    np_img_for_noise = np.array(img_pixelated)
    # Aplicar ruido con un rango pequeño para sutileza
    noise = np.random.randint(-10, 11, np_img_for_noise.shape, dtype=np.int16) 
    np_img_noisy = np.clip(np_img_for_noise.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    effect_img_pil = Image.fromarray(np_img_noisy)

    # 3. Aberración Cromática (si se especifica)
    if chroma_intensity > 0:
        effect_img_pil = apply_chromatic_aberration_on_pil_image(effect_img_pil, chroma_intensity)

    # 4. Cuadro de Diálogo (si se especifica)
    if add_dialog and dialog_text:
        # El diálogo se añade sobre la imagen ya con todos los efectos (incluida aberración)
        canvas_mode = 'RGBA' if effect_img_pil.mode == 'RGBA' else 'RGB'
        canvas_bg_color = (50, 50, 50, 255) if canvas_mode == 'RGBA' else (50, 50, 50)
        dialog_h_pixels = 10 
        dialog_height_actual = current_pixel_size * dialog_h_pixels 
        
        new_total_height = effect_img_pil.height + dialog_height_actual
        canvas = Image.new(canvas_mode, (effect_img_pil.width, new_total_height), canvas_bg_color)
        canvas.paste(effect_img_pil, (0, 0), effect_img_pil if effect_img_pil.mode == 'RGBA' else None)
        
        draw = ImageDraw.Draw(canvas)
        dialog_margin = current_pixel_size
        rect_x0 = dialog_margin * 2
        rect_y0 = effect_img_pil.height + dialog_margin
        rect_x1 = effect_img_pil.width - (dialog_margin * 2)
        rect_y1 = new_total_height - dialog_margin
        dialog_box_fill = (80, 80, 80, 200) if canvas_mode == 'RGBA' else (80, 80, 80)
        dialog_box_outline = (200, 200, 200)
        draw.rectangle((rect_x0, rect_y0, rect_x1, rect_y1), fill=dialog_box_fill, outline=dialog_box_outline, width=max(1, current_pixel_size // 2))
        
        try:
            font_size = max(8, current_pixel_size * 3)
            font = ImageFont.truetype("cour.ttf", font_size) # Courier New
        except IOError:
            try:
                font = ImageFont.truetype("DejaVuSansMono.ttf", font_size)
            except IOError:
                try:
                    font = ImageFont.truetype("arial.ttf", font_size) # Fallback a Arial
                except IOError:
                    print("Advertencia: No se encontraron fuentes (cour.ttf, DejaVuSansMono.ttf, arial.ttf). Usando fuente por defecto.")
                    font = ImageFont.load_default()
        text_color = (0, 200, 0) # Verde retro
        text_x = rect_x0 + dialog_margin
        text_y = rect_y0 + dialog_margin 
        draw.text((text_x, text_y), dialog_text, fill=text_color, font=font)
        effect_img_pil = canvas
    
    # Convertir de vuelta a OpenCV BGR (Pillow RGB -> OpenCV BGR)
    # Si la imagen PIL es RGBA (por aberración o diálogo), convertir a RGB antes de BGR
    if effect_img_pil.mode == 'RGBA':
        effect_img_pil = effect_img_pil.convert('RGB') # Perder alfa aquí si se generó, videos no suelen tener alfa

    return cv2.cvtColor(np.array(effect_img_pil), cv2.COLOR_RGB2BGR)

# --- Funciones de FFmpeg y Video I/O ---
def check_ffmpeg_installed():
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_ffmpeg_video_codec(output_ext_str):
    """Devuelve el codec de video para FFmpeg basado en la extensión."""
    # Ejemplos, pueden necesitar ajustes según los codecs instalados en el sistema
    mapping = {
        'mp4': 'libx264', 'mov': 'libx264', 'mkv': 'libx264',
        'avi': 'libxvid', # XVID para AVI es común
        'webm': 'libvpx-vp9' # VP9 para WebM
    }
    return mapping.get(output_ext_str.lower(), 'libx264') # Default a H.264

def process_video_file(input_video_path, output_video_path_or_dir, args):
    """
    Procesa un archivo de video aplicándole los efectos y guardándolo.
    """
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print(f"Error: No se pudo abrir el video '{input_video_path}'")
        return

    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total_frames == 0 or original_fps == 0 : # Sanity check
        print(f"Error: El video '{input_video_path}' parece no tener frames o FPS válidos.")
        cap.release()
        return

    # Determinar dimensiones de salida
    target_width = args.width if args.width else original_width
    target_height = args.height if args.height else original_height

    # Aplicar relación de aspecto a las dimensiones objetivo ANTES del bucle de frames
    # Esto es para definir el tamaño del canvas de salida. El aspect ratio por frame se aplica después.
    if args.aspect_ratio_val is not None:
        # Si se dan width Y height, priorizar height y ajustar width según aspect ratio
        if args.width and args.height:
            target_width = int(target_height * args.aspect_ratio_val)
        # Si solo se da width, ajustar height
        elif args.width and not args.height:
            target_height = int(target_width / args.aspect_ratio_val)
        # Si solo se da height, ajustar width (ya hecho arriba implícitamente o si width no se dio)
        elif not args.width and args.height:
            target_width = int(target_height * args.aspect_ratio_val)
        # Si no se dan ni width ni height, se aplicará el aspect ratio al frame original dentro del bucle
        # y target_width/height se ajustarán allí.
        # Para el VideoWriter, necesitamos las dimensiones finales después del aspect ratio.
        # Creamos un frame de prueba para obtener dimensiones post-aspect-ratio
        if not (args.width and args.height): # Si no se especificaron ambas dims
            ret_test, frame_test = cap.read()
            if ret_test:
                frame_test_aspect = apply_aspect_ratio_to_frame(frame_test, args.aspect_ratio_val, args.aspect_method)
                target_height_post_ar, target_width_post_ar = frame_test_aspect.shape[:2]
                # Si el usuario no especifico width/height, estas son las dimensiones finales
                if not args.width: target_width = target_width_post_ar
                if not args.height: target_height = target_height_post_ar
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Rebobinar

    target_width = max(1, target_width)
    target_height = max(1, target_height)

    output_fps = args.fps if args.fps else original_fps
    output_fps = max(1.0, output_fps) # FPS no puede ser 0

    # Construir nombre y ruta de salida
    input_p_obj = Path(input_video_path)
    base_name, input_ext_str = input_p_obj.stem, input_p_obj.suffix.lstrip('.')
    
    output_format_str = args.output_format if args.output_format else input_ext_str
    if not output_format_str: output_format_str = 'mp4' # Default a mp4 si no hay extensión

    suffix_details = f"_retro_c{args.colors}_p{args.pixel_size}"
    if args.chroma_intensity > 0:
        suffix_details += f"_ca{args.chroma_intensity:.1f}".replace(".0","") # Evitar .0 para enteros

    output_target_p = Path(output_video_path_or_dir)
    if output_target_p.is_dir() or not output_target_p.suffix:
        output_target_p.mkdir(parents=True, exist_ok=True)
        final_output_filename = f"{base_name}{suffix_details}.{output_format_str.lower()}"
        final_output_video_path = output_target_p / final_output_filename
    else:
        final_output_video_path = output_target_p
        if args.output_format: # Asegurar extensión si se especificó formato
            final_output_video_path = final_output_video_path.with_suffix(f".{args.output_format.lower()}")
        final_output_video_path.parent.mkdir(parents=True, exist_ok=True)

    # Preparar para FFmpeg (audio)
    ffmpeg_available = check_ffmpeg_installed()
    temp_video_file = None

    # Dimensiones para VideoWriter (incluyendo el diálogo si se añade)
    # El tamaño del frame que sale de apply_effects_to_frame puede ser mayor si hay diálogo
    # Necesitamos escribir frames de ese tamaño.
    # Obtener las dimensiones del primer frame procesado para configurar VideoWriter
    
    # Procesar un frame de prueba para obtener dimensiones finales
    # (incluyendo efecto de diálogo si está activo)
    ret_test, frame_test = cap.read()
    if not ret_test:
        print(f"Error: No se pudo leer el primer frame de '{input_video_path}'")
        cap.release()
        return
    
    # Aplicar aspect ratio y reescalado al frame de prueba
    if args.aspect_ratio_val is not None:
        frame_test = apply_aspect_ratio_to_frame(frame_test, args.aspect_ratio_val, args.aspect_method)
    frame_test = cv2.resize(frame_test, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)
    
    processed_frame_test = apply_effects_to_frame(
        frame_test, args.colors, args.pixel_size, 
        args.dialog, args.text, args.chroma_intensity
    )
    output_frame_h, output_frame_w = processed_frame_test.shape[:2]
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Rebobinar el video al inicio

    if ffmpeg_available:
        temp_dir = tempfile.mkdtemp()
        temp_video_file = str(Path(temp_dir) / f"temp_video_for_ffmpeg.{output_format_str.lower()}")
        video_writer_path = temp_video_file
    else:
        video_writer_path = str(final_output_video_path)
        print("Advertencia: FFmpeg no encontrado. El video se guardará sin audio.")

    # Usar codec FFmpeg directamente si es posible, o fourcc para OpenCV
    # OpenCV VideoWriter puede ser limitado con codecs. FFmpeg es más robusto.
    # Por ahora, seguimos usando OpenCV VideoWriter para el video sin audio, y FFmpeg para combinar.
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Default a mp4v, puede ser un problema para otros formatos
    if output_format_str.lower() == 'avi': fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # Considerar usar imageio-ffmpeg o scikit-video para una escritura más robusta si OpenCV falla.

    out_cv = cv2.VideoWriter(video_writer_path, fourcc, output_fps, (output_frame_w, output_frame_h))
    if not out_cv.isOpened():
        print(f"Error: No se pudo crear el archivo de video de salida con OpenCV VideoWriter en '{video_writer_path}'.")
        print("Puede ser un problema con el codec ('mp4v' o 'XVID') o permisos.")
        cap.release()
        if temp_dir and os.path.exists(temp_dir): shutil.rmtree(temp_dir, ignore_errors=True)
        return

    print(f"Procesando video: '{input_p_obj.name}' -> '{final_output_video_path.name}'")
    print(f"  Resolución de salida (frames): {output_frame_w}x{output_frame_h} @ {output_fps:.2f} FPS")
    print(f"  Efectos: {args.colors} colores, pixel {args.pixel_size}, croma {args.chroma_intensity:.1f}".replace(".0",""))


    frames_to_process = total_frames // args.frame_skip
    with tqdm(total=frames_to_process, desc=f"Aplicando efectos a {input_p_obj.name}") as pbar:
        for i in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                break
            if i % args.frame_skip == 0:
                # 1. Aplicar aspect ratio al frame actual
                if args.aspect_ratio_val is not None:
                    frame = apply_aspect_ratio_to_frame(frame, args.aspect_ratio_val, args.aspect_method)
                
                # 2. Redimensionar a las dimensiones objetivo (después del aspect ratio)
                frame = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)
                
                # 3. Aplicar todos los efectos (retro, croma, diálogo)
                processed_frame = apply_effects_to_frame(
                    frame, args.colors, args.pixel_size, 
                    args.dialog, args.text, args.chroma_intensity
                )
                out_cv.write(processed_frame)
                pbar.update(1)
    
    cap.release()
    out_cv.release()

    if ffmpeg_available and temp_video_file:
        print(f"Combinando video procesado con audio original usando FFmpeg...")
        ffmpeg_video_codec = get_ffmpeg_video_codec(output_format_str)
        
        # Comando FFmpeg: '-crf' para calidad, '-preset' para velocidad/compresión
        # Para audio, 'aac' es común, '-b:a' para bitrate.
        # '-shortest' asegura que el video termine con la pista más corta (usualmente el video procesado).
        ffmpeg_command = [
            'ffmpeg', '-y', # Sobrescribir salida sin preguntar
            '-i', temp_video_file,    # Video procesado (sin audio)
            '-i', input_video_path,   # Video original (para el audio)
            '-c:v', ffmpeg_video_codec, # Codec de video para la salida
            '-crf', str(args.video_quality_crf),  # Calidad de video (menor es mejor para x264)
            '-preset', args.ffmpeg_preset, # Preset de codificación
            '-c:a', 'aac',           # Codec de audio (AAC es ampliamente compatible)
            '-b:a', '192k',          # Bitrate de audio (ej: 192k)
            '-map', '0:v:0',         # Mapear video del primer input
            '-map', '1:a:0?',        # Mapear audio del segundo input (el '?' lo hace opcional si no hay audio)
            '-shortest',             # Terminar con la pista más corta
            str(final_output_video_path)
        ]
        try:
            subprocess.run(ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Video final con audio guardado en: {final_output_video_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error durante la combinación con FFmpeg: {e.stderr.decode('utf-8', errors='ignore')}")
            print(f"Se guardará el video sin audio procesado en: {final_output_video_path}")
            import shutil
            shutil.move(temp_video_file, str(final_output_video_path)) # Mover el video sin audio
        finally:
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True) # Limpiar directorio temporal
    elif not ffmpeg_available:
         print(f"Video sin audio guardado en: {final_output_video_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Aplicar efecto retro y aberración cromática a videos.')
    
    parser.add_argument('input_path', help='Ruta al archivo de video o directorio de videos.')
    parser.add_argument('-o', '--output', help='Ruta del archivo de salida o directorio de salida. '
                                               'Por defecto: subdirectorio "pyxelart_video_output".')
    
    # Argumentos de efectos y dimensiones
    parser.add_argument('--width', type=int, help='Ancho de salida de los frames (antes del diálogo).')
    parser.add_argument('--height', type=int, help='Alto de salida de los frames (antes del diálogo).')
    parser.add_argument('--colors', type=int, default=16, help='Número de colores. Por defecto: 16.')
    parser.add_argument('--pixel-size', type=int, default=4, help='Tamaño del "gran píxel". Por defecto: 4.')
    parser.add_argument('--dialog', action='store_true', help='Añadir cuadro de diálogo.')
    parser.add_argument('--text', default='LOADING...', help='Texto para el diálogo. Por defecto: "LOADING...".')
    parser.add_argument('--aspect-ratio', type=str, default='original',
                               help='Relación de aspecto (ej: "4:3", "16:9", "original"). Por defecto: "original".')
    parser.add_argument('--aspect-method', choices=['resize', 'crop'], default='resize',
                               help='Método para ajustar relación de aspecto. Por defecto: "resize".')
    parser.add_argument('--chroma-intensity', type=float, default=0.0,
                               help='Intensidad de aberración cromática (0 para desactivar). Por defecto: 0.0.')

    # Argumentos de video
    parser.add_argument('--frame-skip', type=int, default=1, metavar='N',
                               help='Procesar 1 de cada N frames. Por defecto: 1 (procesar todos).')
    parser.add_argument('--fps', type=float, help='FPS del video de salida. Por defecto: original.')
    parser.add_argument('-f', '--output-format', choices=['mp4', 'avi', 'mov', 'mkv', 'webm'],
                               help='Formato de video de salida (ej: mp4). Por defecto: original o mp4.')
    
    # Argumentos de calidad FFmpeg (usados si FFmpeg está disponible)
    parser.add_argument('--video-quality-crf', type=int, default=23, metavar='CRF',
                               help='Calidad de video para FFmpeg (CRF, ej: para x264, 0-51, menor es mejor). Por defecto: 23.')
    parser.add_argument('--ffmpeg-preset', choices=['ultrafast', 'superfast', 'veryfast', 'faster', 
                                                   'fast', 'medium', 'slow', 'slower', 'veryslow'], 
                               default='medium', help='Preset de codificación FFmpeg (velocidad vs compresión). Por defecto: "medium".')

    args = parser.parse_args()
    
    try:
        args.aspect_ratio_val = parse_aspect_ratio_str(args.aspect_ratio)
        args.pixel_size = max(1, args.pixel_size) # Asegurar pixel_size >= 1
        args.frame_skip = max(1, args.frame_skip) # Asegurar frame_skip >= 1
        
        input_p = Path(args.input_path)

        if not input_p.exists():
            print(f"Error: La ruta de entrada '{args.input_path}' no existe.")
            exit(1)

        default_output_parent_dir = input_p.parent if input_p.is_file() else input_p
        default_output_dir_name = "pyxelart_video_output"

        if input_p.is_file():
            if input_p.suffix.lower() not in SUPPORTED_VIDEO_EXTENSIONS:
                print(f"Error: El archivo '{input_p.name}' no es un video soportado.")
                exit(1)
            
            output_target = args.output
            if not output_target:
                output_target = default_output_parent_dir / default_output_dir_name
                output_target.mkdir(parents=True, exist_ok=True)
            process_video_file(str(input_p), str(output_target), args)

        elif input_p.is_dir():
            output_dir_path = Path(args.output) if args.output else input_p / default_output_dir_name
            output_dir_path.mkdir(parents=True, exist_ok=True)
            
            if not output_dir_path.is_dir():
                 print(f"Error: La entrada es un directorio, pero la ruta de salida '{args.output}' no es un directorio.")
                 exit(1)

            video_files = [f for f in input_p.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED_VIDEO_EXTENSIONS]
            if not video_files:
                print(f"No se encontraron videos soportados en '{str(input_p)}'.")
            else:
                print(f"Encontrados {len(video_files)} videos para procesar en '{str(input_p)}'.")
                args.is_batch_item = True # Para mensajes o lógica interna si es necesario
                for video_file_p_obj in video_files: # tqdm se usa dentro de process_video_file
                    print("-" * 50) # Separador visual para cada video en lote
                    process_video_file(str(video_file_p_obj), str(output_dir_path), args)
                print("-" * 50)
                print(f"\nProceso por lotes completo. Resultados guardados en: {str(output_dir_path)}")
        else:
            print(f"Error: La ruta '{args.input_path}' no es un archivo ni un directorio reconocible.")

    except ValueError as ve:
        print(f"Error de validación: {ve}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        import traceback
        traceback.print_exc()

