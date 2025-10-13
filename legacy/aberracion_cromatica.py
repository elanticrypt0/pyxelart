# -*- coding: utf-8 -*-
# Script para generar un efecto de aberración cromática.
# Modificado para procesar archivos individuales o directorios y guardar en una carpeta de salida.
#
# Para instalar las dependencias usando uv (o pip):
# uv pip install Pillow
# pip install Pillow
#
# Ejemplo de uso (modificado):
# python aberracion_cromatica_modificado.py mi_imagen.jpg -od ./salida_aberracion
# python aberracion_cromatica_modificado.py ./mi_directorio_imagenes -od ./salida_aberracion --intensity 10 --format webp

import argparse
import os
import math
from PIL import Image

SUPPORTED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')


def get_pixel_value_with_edges(pixels, x, y, width, height, mode, default_channel_value_if_edge):
    """
    Obtiene el valor del píxel (para un solo canal) manejando los bordes según el modo.
    `default_channel_value_if_edge` es el valor a usar si el modo es black(0) o white(255)
    o 0 si es transparent (el alfa se encargará).
    """
    # Asegurarse de que x e y sean enteros para el acceso a píxeles
    x_int, y_int = int(round(x)), int(round(y))

    if mode == 'clamp':
        x_clamped = max(0, min(x_int, width - 1))
        y_clamped = max(0, min(y_int, height - 1))
        return pixels[x_clamped, y_clamped]

    if 0 <= x_int < width and 0 <= y_int < height:
        return pixels[x_int, y_int]
    else:
        # Para 'transparent', 'black', 'white', el valor del canal de color es el mismo
        # si está fuera de los límites. El manejo del alfa es separado.
        return default_channel_value_if_edge


def apply_chromatic_aberration_effect(
        image_obj,  # Modificado: recibe un objeto Image de Pillow
        intensity,
        red_shift_factors, green_shift_factors, blue_shift_factors,
        lens_effect, lens_center_rel, lens_falloff,
        edge_mode
):
    """
    Aplica el efecto de aberración cromática a un objeto Imagen.
    Modificado para devolver el objeto Imagen procesado en lugar de guardarlo.
    """
    img_rgba = image_obj.convert("RGBA")  # Trabajar siempre con RGBA internamente
    width, height = img_rgba.size

    output_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    r_orig, g_orig, b_orig, a_orig = img_rgba.split()
    pixels_r_orig = r_orig.load()
    pixels_g_orig = g_orig.load()
    pixels_b_orig = b_orig.load()
    pixels_a_orig = a_orig.load()
    pixels_out = output_img.load()

    center_x_abs = width * lens_center_rel[0]
    center_y_abs = height * lens_center_rel[1]

    corners = [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]
    max_dist_sq = 0
    for cx, cy in corners:
        dist_sq = (cx - center_x_abs) ** 2 + (cy - center_y_abs) ** 2
        max_dist_sq = max(max_dist_sq, dist_sq)
    max_dist = math.sqrt(max_dist_sq) if max_dist_sq > 0 else 1.0

    default_edge_color_val = 0
    if edge_mode == 'white':
        default_edge_color_val = 255

    for y_out in range(height):
        for x_out in range(width):
            scale_factor = 1.0
            if lens_effect:
                dist_x = x_out - center_x_abs
                dist_y = y_out - center_y_abs
                current_dist = math.sqrt(dist_x ** 2 + dist_y ** 2)
                norm_dist = current_dist / max_dist
                if lens_falloff == 'linear':
                    scale_factor = norm_dist
                elif lens_falloff == 'quadratic':
                    scale_factor = norm_dist ** 2
                scale_factor = min(1.0, max(0.0, scale_factor))

            dr_x = intensity * red_shift_factors[0] * scale_factor
            dr_y = intensity * red_shift_factors[1] * scale_factor
            dg_x = intensity * green_shift_factors[0] * scale_factor
            dg_y = intensity * green_shift_factors[1] * scale_factor
            db_x = intensity * blue_shift_factors[0] * scale_factor
            db_y = intensity * blue_shift_factors[1] * scale_factor

            src_rx, src_ry = x_out - dr_x, y_out - dr_y
            src_gx, src_gy = x_out - dg_x, y_out - dg_y
            src_bx, src_by = x_out - db_x, y_out - db_y

            val_r = get_pixel_value_with_edges(pixels_r_orig, src_rx, src_ry, width, height, edge_mode,
                                               default_edge_color_val)
            val_g = get_pixel_value_with_edges(pixels_g_orig, src_gx, src_gy, width, height, edge_mode,
                                               default_edge_color_val)
            val_b = get_pixel_value_with_edges(pixels_b_orig, src_bx, src_by, width, height, edge_mode,
                                               default_edge_color_val)

            current_alpha = pixels_a_orig[x_out, y_out]
            if edge_mode == 'transparent':
                is_r_out = not (0 <= round(src_rx) < width and 0 <= round(src_ry) < height)
                is_g_out = not (0 <= round(src_gx) < width and 0 <= round(src_gy) < height)
                is_b_out = not (0 <= round(src_bx) < width and 0 <= round(src_by) < height)
                if is_r_out or is_g_out or is_b_out:
                    current_alpha = 0
            pixels_out[x_out, y_out] = (val_r, val_g, val_b, current_alpha)

    return output_img  # Devuelve el objeto imagen procesado


def process_single_image(filepath, output_dir, args):
    """
    Carga una imagen, aplica el efecto de aberración cromática y la guarda.
    """
    try:
        original_img = Image.open(filepath)
        filename = os.path.basename(filepath)
        name, _ = os.path.splitext(filename)

        print(f"Procesando '{filename}' para aberración cromática...")

        # Aplicar el efecto
        processed_img = apply_chromatic_aberration_effect(
            original_img,
            args.intensity,
            args.red_shift, args.green_shift, args.blue_shift,
            args.lens_effect, args.lens_center, args.lens_falloff,
            args.edge_mode
        )

        # Guardar la imagen
        output_format = args.output_format.lower()
        output_filename = f"{name}_aberration.{output_format}"
        output_path = os.path.join(output_dir, output_filename)

        final_save_img = processed_img
        save_params = {}

        if output_format == 'jpeg' or output_format == 'jpg':
            if final_save_img.mode == 'RGBA':
                print(f"  Convirtiendo a RGB para formato {output_format.upper()} (elimina transparencia).")
                # Crear una nueva imagen RGB con fondo.
                bg_color_for_jpeg = (0, 0, 0)  # Negro por defecto para JPEG
                if args.edge_mode == 'white':  # O un color de fondo predeterminado si es relevante
                    bg_color_for_jpeg = (255, 255, 255)

                rgb_image = Image.new("RGB", final_save_img.size, bg_color_for_jpeg)
                rgb_image.paste(final_save_img, mask=final_save_img.split()[3])
                final_save_img = rgb_image
            save_params['quality'] = args.quality
            save_params['progressive'] = True
            save_params['optimize'] = True
        elif output_format == 'webp':
            save_params['quality'] = args.quality
            if args.quality == 100:
                save_params['lossless'] = True
        elif output_format == 'png':
            png_compress_level = max(0, min(9, 9 - int((args.quality - 1) / 11)))
            save_params['compress_level'] = png_compress_level
            save_params['optimize'] = True

        final_save_img.save(output_path, format=output_format.upper(), **save_params)
        print(f"  Imagen con aberración cromática guardada como: {output_path}")

    except FileNotFoundError:
        print(f"Error: Archivo no encontrado - {filepath}")
    except Exception as e:
        print(f"Error procesando {filepath}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Aplica un efecto de aberración cromática a una imagen o a todas las imágenes en un directorio.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("input_path", help="Ruta a la imagen de entrada o directorio de imágenes.")
    parser.add_argument("-od", "--output_dir", default="output_aberration",
                        help="Directorio para guardar las imágenes procesadas.")

    parser.add_argument("-f", "--output_format", choices=['png', 'webp', 'jpeg', 'jpg'], default='png',
                        help="Formato de la imagen de salida.")
    parser.add_argument("-q", "--quality", type=int, default=90, choices=range(1, 101), metavar="[1-100]",
                        help="Calidad de la imagen de salida (1-100). Para PNG, afecta la compresión.")

    # Argumentos específicos del efecto (mantenidos del script original)
    parser.add_argument("-i", "--intensity", type=float, default=5.0,
                        help="Intensidad base del desplazamiento en píxeles.")
    parser.add_argument("-rs", "--red-shift", type=float, nargs=2, default=[1.0, 0.0],
                        metavar=('DX_FACTOR', 'DY_FACTOR'),
                        help="Factores de desplazamiento (dx dy) para el canal Rojo, multiplicados por la intensidad.")
    parser.add_argument("-gs", "--green-shift", type=float, nargs=2, default=[0.0, 0.0],
                        metavar=('DX_FACTOR', 'DY_FACTOR'),
                        help="Factores de desplazamiento (dx dy) para el canal Verde.")
    parser.add_argument("-bs", "--blue-shift", type=float, nargs=2, default=[-1.0, 0.0],
                        metavar=('DX_FACTOR', 'DY_FACTOR'),
                        help="Factores de desplazamiento (dx dy) para el canal Azul.")
    parser.add_argument("--lens-effect", action='store_true',
                        help="Activar efecto de lente (más fuerte en los bordes, más débil en el centro).")
    parser.add_argument("--lens-center", type=float, nargs=2, default=[0.5, 0.5], metavar=('CX_REL', 'CY_REL'),
                        help="Centro del efecto de lente como porcentaje del ancho/alto (0.0-1.0).")
    parser.add_argument("--lens-falloff", choices=['linear', 'quadratic'], default='linear',
                        help="Cómo disminuye el efecto hacia el centro ('linear' o 'quadratic').")
    parser.add_argument("--edge-mode", choices=['transparent', 'black', 'white', 'clamp'], default='transparent',
                        help="Comportamiento en los bordes: 'transparent', 'black', 'white', 'clamp'.")

    args = parser.parse_args()

    if not (0.0 <= args.lens_center[0] <= 1.0 and 0.0 <= args.lens_center[1] <= 1.0):
        parser.error("--lens-center los valores deben estar entre 0.0 y 1.0.")

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        print(f"Directorio de salida creado: {args.output_dir}")

    if os.path.isfile(args.input_path):
        if args.input_path.lower().endswith(SUPPORTED_EXTENSIONS):
            process_single_image(args.input_path, args.output_dir, args)
        else:
            print(f"Omitiendo archivo no soportado: {args.input_path}")
    elif os.path.isdir(args.input_path):
        print(f"Procesando directorio: {args.input_path}")
        for item in os.listdir(args.input_path):
            item_path = os.path.join(args.input_path, item)
            if os.path.isfile(item_path) and item.lower().endswith(SUPPORTED_EXTENSIONS):
                process_single_image(item_path, args.output_dir, args)
            elif os.path.isfile(item_path):
                print(f"Omitiendo archivo con extensión no soportada: {item_path}")
    else:
        print(f"Error: La ruta de entrada '{args.input_path}' no es un archivo ni un directorio válido.")


if __name__ == "__main__":
    main()
