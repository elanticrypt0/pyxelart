#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops
import argparse
import os
from pathlib import Path
from tqdm import tqdm  # Para la barra de progreso

SUPPORTED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')


def apply_aspect_ratio_util(img, target_ratio, method='resize'):
    """
    Aplica una relación de aspecto específica a la imagen.
    """
    width, height = img.size
    current_ratio = width / height

    if abs(current_ratio - target_ratio) < 0.01:
        return img

    if method == 'resize':
        new_width = int(height * target_ratio)
        if new_width == 0: new_width = 1
        return img.resize((new_width, height), Image.Resampling.LANCZOS)

    elif method == 'crop':
        if current_ratio > target_ratio:
            new_w = int(height * target_ratio)
            if new_w == 0: new_w = 1
            x_offset = (width - new_w) // 2
            return img.crop((x_offset, 0, x_offset + new_w, height))
        else:
            new_h = int(width / target_ratio)
            if new_h == 0: new_h = 1
            y_offset = (height - new_h) // 2
            return img.crop((0, y_offset, width, y_offset + new_h))
    return img


def parse_aspect_ratio_str(aspect_str):
    """Convierte una cadena de relación de aspecto a un valor numérico."""
    if aspect_str is None or aspect_str.lower() == "original":
        return None
    if aspect_str == "4:3":
        return 4 / 3
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


def apply_chromatic_aberration_effect_util(image_obj, intensity):
    """
    Aplica un efecto de aberración cromática simple a un objeto Image.
    La intensidad controla el desplazamiento de los canales.
    """
    if intensity == 0:
        return image_obj

    img_copy = image_obj.copy()
    if img_copy.mode != 'RGBA':
        img_copy = img_copy.convert('RGBA')  # Necesario para separar canales y preservar alfa si existe

    r, g, b, a = img_copy.split()

    # Desplazamiento basado en la intensidad. Puede ser ajustado para diferentes looks.
    # Un desplazamiento entero es más nítido para pixel art.
    offset = int(round(intensity))

    # Desplazar Rojo a la izquierda, Azul a la derecha. Verde se queda.
    r_shifted = ImageChops.offset(r, -offset, 0)
    b_shifted = ImageChops.offset(b, offset, 0)

    # Volver a fusionar los canales
    return Image.merge('RGBA', (r_shifted, g, b_shifted, a))


def apply_retro_filter_to_image(img_obj, color_depth=16, pixel_size=4,
                                add_dialog=False, dialog_text="",
                                original_has_alpha=False,
                                chroma_intensity=0):  # Nuevo parámetro
    """
    Aplica el filtro retro principal y opcionalmente la aberración cromática.
    """
    processed_img = img_obj.copy()

    if original_has_alpha:
        rgb_component = processed_img.convert('RGB')
        alpha_component = processed_img.split()[-1]
        rgb_quantized = rgb_component.quantize(colors=color_depth, method=Image.Quantize.MEDIANCUT)
        rgb_quantized = rgb_quantized.convert('RGB')
        pixel_width = max(1, rgb_quantized.width // pixel_size)
        pixel_height = max(1, rgb_quantized.height // pixel_size)
        rgb_pixelated = rgb_quantized.resize((pixel_width, pixel_height), Image.Resampling.NEAREST)
        rgb_pixelated = rgb_pixelated.resize((rgb_quantized.width, rgb_quantized.height), Image.Resampling.NEAREST)
        alpha_pixelated = alpha_component.resize((pixel_width, pixel_height), Image.Resampling.NEAREST)
        alpha_pixelated = alpha_pixelated.resize((rgb_pixelated.width, rgb_pixelated.height), Image.Resampling.NEAREST)
        np_rgb = np.array(rgb_pixelated)
        noise = np.random.randint(-10, 11, np_rgb.shape, dtype=np.int16)
        np_rgb = np.clip(np_rgb.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        rgb_with_noise = Image.fromarray(np_rgb)
        final_effect_img = Image.merge('RGBA', (*rgb_with_noise.split(), alpha_pixelated))
    else:
        img_quantized = processed_img.convert('RGB').quantize(colors=color_depth, method=Image.Quantize.MEDIANCUT)
        img_quantized = img_quantized.convert('RGB')
        pixel_width = max(1, img_quantized.width // pixel_size)
        pixel_height = max(1, img_quantized.height // pixel_size)
        img_pixelated = img_quantized.resize((pixel_width, pixel_height), Image.Resampling.NEAREST)
        img_pixelated = img_pixelated.resize((img_quantized.width, img_quantized.height), Image.Resampling.NEAREST)
        np_img = np.array(img_pixelated)
        noise = np.random.randint(-10, 11, np_img.shape, dtype=np.int16)
        np_img = np.clip(np_img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        final_effect_img = Image.fromarray(np_img)

    # Aplicar aberración cromática si la intensidad es > 0
    if chroma_intensity > 0:
        final_effect_img = apply_chromatic_aberration_effect_util(final_effect_img, chroma_intensity)

    if add_dialog and dialog_text:
        # Determinar el modo del canvas basado en si la imagen final (después de aberración) tiene alfa
        canvas_mode = 'RGBA' if final_effect_img.mode == 'RGBA' else 'RGB'
        canvas_bg_color = (50, 50, 50, 255) if canvas_mode == 'RGBA' else (50, 50, 50)
        dialog_h_pixels = 10
        dialog_height_actual = pixel_size * dialog_h_pixels
        new_total_height = final_effect_img.height + dialog_height_actual
        canvas = Image.new(canvas_mode, (final_effect_img.width, new_total_height), canvas_bg_color)
        canvas.paste(final_effect_img, (0, 0), final_effect_img if final_effect_img.mode == 'RGBA' else None)
        draw = ImageDraw.Draw(canvas)
        dialog_margin = pixel_size
        rect_x0 = dialog_margin * 2
        rect_y0 = final_effect_img.height + dialog_margin
        rect_x1 = final_effect_img.width - (dialog_margin * 2)
        rect_y1 = new_total_height - dialog_margin
        dialog_box_fill = (80, 80, 80, 200) if canvas_mode == 'RGBA' else (80, 80, 80)
        dialog_box_outline = (200, 200, 200)
        draw.rectangle((rect_x0, rect_y0, rect_x1, rect_y1), fill=dialog_box_fill, outline=dialog_box_outline,
                       width=max(1, pixel_size // 2))
        try:
            font_size = max(8, pixel_size * 3)
            font = ImageFont.truetype("cour.ttf", font_size)
        except IOError:
            try:
                font = ImageFont.truetype("DejaVuSansMono.ttf", font_size)
            except IOError:
                print(
                    "Advertencia: No se encontraron fuentes monoespaciadas (cour.ttf, DejaVuSansMono.ttf). Usando fuente por defecto.")
                font = ImageFont.load_default()
        text_color = (0, 200, 0)
        text_x = rect_x0 + dialog_margin
        text_y = rect_y0 + dialog_margin
        draw.text((text_x, text_y), dialog_text, fill=text_color, font=font)
        final_effect_img = canvas

    return final_effect_img


def process_and_save_image(input_filepath, output_path_or_dir, args):
    """
    Procesa una imagen individual y la guarda.
    output_path_or_dir puede ser una ruta de archivo o un directorio.
    """
    try:
        img = Image.open(input_filepath)
    except FileNotFoundError:
        print(f"Error: Archivo no encontrado - {input_filepath}")
        return
    except Exception as e:
        print(f"Error al abrir la imagen {input_filepath}: {e}")
        return

    filename = Path(input_filepath).name
    base_name, input_ext = Path(input_filepath).stem, Path(input_filepath).suffix

    # Determinar si el modo de procesamiento es 'single_file' o 'batch_item'
    # Esto solo afecta la verbosidad del print, el procesamiento es el mismo.
    processing_mode_msg = "Procesando archivo" if not hasattr(args, 'is_batch_item') else "Procesando"
    print(f"{processing_mode_msg}: '{filename}' para efecto retro...")

    original_has_alpha = img.mode == 'RGBA' or (img.mode == 'P' and 'A' in img.info.get('transparency', {}))

    if args.aspect_ratio_val is not None:
        img = apply_aspect_ratio_util(img, args.aspect_ratio_val, args.aspect_method)

    if args.width and args.height:
        target_w = max(1, args.width)
        target_h = max(1, args.height)
        img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    current_pixel_size = max(1, args.pixel_size)
    processed_img = apply_retro_filter_to_image(
        img, args.colors, current_pixel_size, args.dialog, args.text,
        original_has_alpha, args.chroma_intensity
    )

    output_format_ext = args.output_format if args.output_format else input_ext.lstrip('.')
    if not output_format_ext: output_format_ext = 'png'

    suffix_details = f"_retro_c{args.colors}_p{current_pixel_size}"
    if args.chroma_intensity > 0:
        suffix_details += f"_ca{args.chroma_intensity}"

    output_p = Path(output_path_or_dir)
    if output_p.is_dir() or not output_p.suffix:  # Si es un directorio o no tiene extensión (asumimos dir)
        output_p.mkdir(parents=True, exist_ok=True)  # Asegurar que el directorio exista
        output_filename = f"{base_name}{suffix_details}.{output_format_ext.lower()}"
        final_output_path = output_p / output_filename
    else:  # Es una ruta de archivo completa
        final_output_path = output_p
        # Asegurar que la extensión coincida con output_format si se especificó
        if args.output_format:
            final_output_path = final_output_path.with_suffix(f".{args.output_format.lower()}")
        final_output_path.parent.mkdir(parents=True, exist_ok=True)

    save_options = {}
    final_save_image = processed_img
    actual_save_format = final_output_path.suffix.lstrip('.').upper()
    if not actual_save_format: actual_save_format = output_format_ext.upper()

    if actual_save_format in ['JPEG', 'JPG']:
        actual_save_format = 'JPEG'
        if final_save_image.mode == 'RGBA' or final_save_image.mode == 'LA' or \
                (final_save_image.mode == 'P' and original_has_alpha):
            print(f"  Aviso: {filename} - El formato JPEG no soporta transparencia. Se convertirá a RGB.")
            # Crear una nueva imagen RGB con fondo blanco y pegar la imagen RGBA sobre ella
            bg_image = Image.new("RGB", final_save_image.size, (255, 255, 255))
            bg_image.paste(final_save_image,
                           mask=final_save_image.split()[-1] if final_save_image.mode in ['RGBA', 'LA'] else None)
            final_save_image = bg_image

        save_options['quality'] = args.quality
        save_options['optimize'] = True
    elif actual_save_format == 'PNG':
        save_options['optimize'] = True
        save_options['compress_level'] = max(0,
                                             min(9, int(9 - (args.quality - 1) * 8 / 99))) if args.quality < 100 else 1
    elif actual_save_format == 'WEBP':
        save_options['quality'] = args.quality
        save_options['lossless'] = (args.quality == 100)
        if final_save_image.mode == 'RGBA' or final_save_image.mode == 'LA':
            save_options['exact'] = True

    try:
        final_save_image.save(str(final_output_path), format=actual_save_format, **save_options)
        print(f"  Imagen procesada guardada en: {str(final_output_path)}")
    except Exception as e:
        print(f"  Error al guardar {str(final_output_path)} como {actual_save_format}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Aplicar efecto retro (pixel art) y aberración cromática a imágenes.')

    parser.add_argument('input_path', help='Ruta al archivo de imagen o directorio de imágenes de entrada.')
    parser.add_argument('-o', '--output', help='Ruta del archivo de salida o directorio de salida. '
                                               'Si input_path es un archivo y --output es un dir, se genera nombre. '
                                               'Si input_path es dir, --output debe ser un dir. '
                                               'Por defecto: subdirectorio "pyxelart_output".')

    # Argumentos comunes del efecto
    parser.add_argument('--width', type=int, help='Ancho de salida en píxeles.')
    parser.add_argument('--height', type=int, help='Alto de salida en píxeles.')
    parser.add_argument('--colors', type=int, default=16, help='Profundidad de color (ej: 8, 16, 32). Por defecto: 16.')
    parser.add_argument('--pixel-size', type=int, default=4, help='Tamaño del "gran píxel" retro. Por defecto: 4.')
    parser.add_argument('--dialog', action='store_true', help='Añadir un cuadro de diálogo estilo retro.')
    parser.add_argument('--text', default='GAME OVER',
                        help='Texto para el cuadro de diálogo. Por defecto: "GAME OVER".')
    parser.add_argument('--aspect-ratio', type=str, default='original',
                        help='Relación de aspecto (ej: "4:3", "1:1", "original"). Por defecto: "original".')
    parser.add_argument('--aspect-method', choices=['resize', 'crop'], default='resize',
                        help='Método para ajustar relación de aspecto. Por defecto: "resize".')
    parser.add_argument('--chroma-intensity', type=float, default=0.0,
                        help='Intensidad de la aberración cromática (0 para desactivar). Por defecto: 0.0.')
    parser.add_argument('-q', '--quality', type=int, default=95, choices=range(1, 101), metavar="[1-100]",
                        help='Calidad para JPEG/WEBP y compresión para PNG (1-100). Por defecto: 95.')
    parser.add_argument('-f', '--output-format', choices=['png', 'jpg', 'jpeg', 'webp'],
                        help='Formato de salida explícito. Por defecto: original o PNG.')

    args = parser.parse_args()

    try:
        args.aspect_ratio_val = parse_aspect_ratio_str(args.aspect_ratio)

        input_p = Path(args.input_path)

        if not input_p.exists():
            print(f"Error: La ruta de entrada '{args.input_path}' no existe.")
            exit(1)

        if input_p.is_file():
            if input_p.suffix.lower() not in SUPPORTED_EXTENSIONS:
                print(f"Error: El archivo '{input_p.name}' no tiene una extensión de imagen soportada.")
                exit(1)

            output_target = args.output
            if not output_target:  # No se dio -o, crear subdir por defecto
                output_target = input_p.parent / "pyxelart_output"
                output_target.mkdir(parents=True, exist_ok=True)
            # process_and_save_image se encarga de si output_target es archivo o dir
            process_and_save_image(str(input_p), str(output_target), args)

        elif input_p.is_dir():
            output_dir_path = Path(args.output) if args.output else input_p / "pyxelart_output"
            output_dir_path.mkdir(parents=True, exist_ok=True)

            if not output_dir_path.is_dir():  # Si args.output era un archivo pero la entrada es un dir
                print(
                    f"Error: La entrada es un directorio, pero la ruta de salida '{args.output}' no es un directorio.")
                exit(1)

            image_files = [f for f in input_p.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS]

            if not image_files:
                print(f"No se encontraron imágenes soportadas en '{str(input_p)}'.")
            else:
                print(f"Encontradas {len(image_files)} imágenes para procesar en '{str(input_p)}'.")
                # Marcar que es un item de batch para la lógica de mensajes/nombres si es necesario
                args.is_batch_item = True
                for file_path_obj in tqdm(image_files, desc="Procesando imágenes"):
                    process_and_save_image(str(file_path_obj), str(output_dir_path), args)
                print(f"\nProceso completo. Resultados guardados en: {str(output_dir_path)}")
        else:
            print(f"Error: La ruta de entrada '{args.input_path}' no es un archivo ni un directorio reconocible.")

    except ValueError as ve:
        print(f"Error de validación: {ve}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        import traceback

        traceback.print_exc()

