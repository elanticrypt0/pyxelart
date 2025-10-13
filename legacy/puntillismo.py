# -*- coding: utf-8 -*-
# Script para convertir una imagen a estilo puntillismo.
# Modificado para procesar archivos individuales o directorios y guardar en una carpeta de salida.
#
# Para instalar las dependencias usando uv:
# uv pip install Pillow numpy
#
# Ejemplo de uso (modificado):
# python puntillismo_modificado.py mi_imagen.jpg -od ./salida_puntillismo
# python puntillismo_modificado.py ./mi_directorio_imagenes -od ./salida_puntillismo --dot-size 7 --format png

import argparse
import os
import random
from PIL import Image, ImageDraw, ImageStat

# import numpy as np # NumPy es opcional si no se usa 'average' o para optimizarlo.

SUPPORTED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')


def hex_to_rgb(hex_color):
    """Convierte un color hexadecimal a una tupla RGB."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])
    if len(hex_color) != 6:
        raise ValueError("Entrada de color hexadecimal inválida.")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def parse_background_color(color_str, target_mode='RGB'):
    """Analiza la cadena de color de fondo y la devuelve en el formato correcto."""
    if color_str.lower() == 'transparent':
        if target_mode == 'RGBA':
            return (0, 0, 0, 0)
        else:
            print("Advertencia: Fondo transparente solicitado pero el modo de salida no es RGBA. Usando blanco.")
            return (255, 255, 255)
    if color_str.startswith('#'):
        try:
            return hex_to_rgb(color_str)
        except ValueError:
            print(f"Advertencia: Color hexadecimal '{color_str}' inválido. Usando blanco.")
            return (255, 255, 255)
    return color_str


def apply_pointillist_effect(image_obj,  # Modificado: recibe un objeto Image
                             dot_size, spacing_ratio, color_sample_mode,
                             bg_color_str, jitter_strength):
    """
    Aplica el efecto puntillista a un objeto Imagen.
    Modificado para devolver el objeto Imagen procesado.
    """
    output_mode = 'RGB'
    # Comprobación simple: si el color de fondo es transparente, la salida debería ser RGBA.
    # O si la imagen original tiene un canal alfa y el formato de salida lo permite (como PNG por defecto)
    if bg_color_str.lower() == 'transparent' or ('A' in image_obj.mode and output_mode != 'JPEG'):
        output_mode = 'RGBA'

    img_for_sampling = image_obj.convert(
        output_mode if output_mode == 'RGBA' else 'RGB')  # Asegurar el modo correcto para el muestreo

    bg_color_parsed = parse_background_color(bg_color_str, output_mode)
    output_img = Image.new(output_mode, image_obj.size, bg_color_parsed)
    draw = ImageDraw.Draw(output_img)

    width, height = image_obj.size
    radius = dot_size // 2
    step = max(1, int(dot_size * spacing_ratio))

    for y in range(0, height, step):
        for x in range(0, width, step):
            center_x = x + random.uniform(-jitter_strength, jitter_strength) * step
            center_y = y + random.uniform(-jitter_strength, jitter_strength) * step
            sample_x = int(max(0, min(center_x, width - 1)))
            sample_y = int(max(0, min(center_y, height - 1)))

            dot_color = None
            if color_sample_mode == 'direct':
                dot_color = img_for_sampling.getpixel((sample_x, sample_y))
            elif color_sample_mode == 'average':
                avg_box_left = max(0, sample_x - radius)
                avg_box_top = max(0, sample_y - radius)
                avg_box_right = min(width, sample_x + radius + 1)
                avg_box_bottom = min(height, sample_y + radius + 1)
                if avg_box_left < avg_box_right and avg_box_top < avg_box_bottom:
                    region = img_for_sampling.crop((avg_box_left, avg_box_top, avg_box_right, avg_box_bottom))
                    if region.size[0] > 0 and region.size[1] > 0:
                        try:
                            stat = ImageStat.Stat(region)
                            mean_values = stat.mean[:len(img_for_sampling.mode)]
                            dot_color = tuple(int(c) for c in mean_values)
                        except Exception:
                            dot_color = img_for_sampling.getpixel((sample_x, sample_y))
                    else:
                        dot_color = img_for_sampling.getpixel((sample_x, sample_y))
                else:
                    dot_color = img_for_sampling.getpixel((sample_x, sample_y))

            if dot_color:
                # Asegurar que el color tenga la cantidad correcta de canales para el modo de dibujo
                if output_mode == 'RGB' and len(dot_color) == 4:
                    dot_color = dot_color[:3]  # Tomar solo RGB
                elif output_mode == 'RGBA' and len(dot_color) == 3:
                    dot_color = dot_color + (255,)  # Añadir alfa opaco si falta

                draw_x0 = center_x - radius
                draw_y0 = center_y - radius
                draw_x1 = center_x + radius
                draw_y1 = center_y + radius
                draw.ellipse([draw_x0, draw_y0, draw_x1, draw_y1], fill=dot_color)
    return output_img


def process_single_image_pointillism(filepath, output_dir, args):
    """
    Carga una imagen, aplica el efecto puntillista y la guarda.
    """
    try:
        original_img = Image.open(filepath)
        filename = os.path.basename(filepath)
        name, _ = os.path.splitext(filename)

        print(f"Procesando '{filename}' para puntillismo...")

        processed_img = apply_pointillist_effect(
            original_img,
            args.dot_size, args.spacing_ratio, args.color_sample,
            args.bg_color, args.jitter
        )

        # Guardar la imagen
        output_format = args.output_format.lower()
        output_filename = f"{name}_pointillist.{output_format}"
        output_path = os.path.join(output_dir, output_filename)

        save_params = {}
        final_save_img = processed_img

        # Adaptar el modo de la imagen si es necesario antes de guardar
        if (output_format == 'jpeg' or output_format == 'jpg') and final_save_img.mode == 'RGBA':
            print(f"  Convirtiendo a RGB para formato {output_format.upper()} (elimina transparencia).")
            # Si el color de fondo original era transparente, usamos blanco para JPEG.
            # De lo contrario, intentamos usar el color de fondo parseado (si no es transparente).
            bg_save_color = (255, 255, 255)  # Blanco por defecto para JPEG si el fondo era transparente
            if args.bg_color.lower() != 'transparent':
                try:
                    parsed_bg = parse_background_color(args.bg_color, 'RGB')
                    if isinstance(parsed_bg, tuple):  # Si es una tupla RGB
                        bg_save_color = parsed_bg
                except:  # En caso de error al parsear, se queda con blanco
                    pass

            rgb_image = Image.new("RGB", final_save_img.size, bg_save_color)
            rgb_image.paste(final_save_img, mask=final_save_img.split()[3])
            final_save_img = rgb_image

        if output_format == 'jpeg' or output_format == 'jpg':
            save_params['quality'] = args.quality
            save_params['optimize'] = True
        elif output_format == 'webp':
            save_params['quality'] = args.quality
            if args.quality == 100 and final_save_img.mode != 'RGBA':  # Lossless WebP no siempre es bueno con alfa
                save_params['lossless'] = True
        elif output_format == 'png':
            png_compress_level = max(0, min(9, 9 - int((args.quality - 1) / 11)))
            save_params['compress_level'] = png_compress_level
            save_params['optimize'] = True

        final_save_img.save(output_path, format=output_format.upper(), **save_params)
        print(f"  Imagen puntillista guardada como: {output_path}")

    except FileNotFoundError:
        print(f"Error: Archivo no encontrado - {filepath}")
    except Exception as e:
        print(f"Error procesando {filepath}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Convierte una imagen a estilo puntillismo, o todas las imágenes en un directorio.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("input_path", help="Ruta a la imagen de entrada o directorio de imágenes.")
    parser.add_argument("-od", "--output_dir", default="output_pointillism",
                        help="Directorio para guardar las imágenes procesadas.")

    parser.add_argument("-f", "--output_format", choices=['webp', 'png', 'jpeg', 'jpg'], default='webp',
                        help="Formato de la imagen de salida.")
    parser.add_argument("-q", "--quality", type=int, default=80, choices=range(1, 101), metavar="[1-100]",
                        help="Calidad de la imagen de salida (1-100).")

    # Argumentos específicos del efecto
    parser.add_argument("-ds", "--dot-size", type=int, default=5,
                        help="Diámetro de los puntos en píxeles.")
    parser.add_argument("-sr", "--spacing-ratio", type=float, default=0.8,
                        help="Relación de espaciado/solapamiento (<1 solapa, >1 separa).")
    parser.add_argument("-cs", "--color-sample", choices=['direct', 'average'], default='direct',
                        help="Método de muestreo de color.")
    parser.add_argument("-bg", "--bg-color", type=str, default='white',
                        help="Color de fondo (nombre CSS, hex #RRGGBB, o 'transparent').")
    parser.add_argument("-j", "--jitter", type=float, default=0.5,
                        help="Factor de aleatoriedad en la posición del punto (0.0-1.0).")

    args = parser.parse_args()

    if args.dot_size <= 0:
        parser.error("--dot-size debe ser un entero positivo.")
    if not (0.0 <= args.jitter <= 1.0):
        parser.error("--jitter debe estar entre 0.0 y 1.0.")

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        print(f"Directorio de salida creado: {args.output_dir}")

    if os.path.isfile(args.input_path):
        if args.input_path.lower().endswith(SUPPORTED_EXTENSIONS):
            process_single_image_pointillism(args.input_path, args.output_dir, args)
        else:
            print(f"Omitiendo archivo no soportado: {args.input_path}")
    elif os.path.isdir(args.input_path):
        print(f"Procesando directorio: {args.input_path}")
        for item in os.listdir(args.input_path):
            item_path = os.path.join(args.input_path, item)
            if os.path.isfile(item_path) and item.lower().endswith(SUPPORTED_EXTENSIONS):
                process_single_image_pointillism(item_path, args.output_dir, args)
            elif os.path.isfile(item_path):
                print(f"Omitiendo archivo con extensión no soportada: {item_path}")
    else:
        print(f"Error: La ruta de entrada '{args.input_path}' no es un archivo ni un directorio válido.")


if __name__ == "__main__":
    main()
