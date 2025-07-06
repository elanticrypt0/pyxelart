# Corrección en image_blureffect.py
import argparse
import os
from PIL import Image, ImageFilter
import numpy as np


def apply_light_trail_effect(image_path, output_dir, effect_amount, output_format='jpg', quality=90):
    try:
        img = Image.open(image_path).convert("RGB")
    except FileNotFoundError:
        print(f"Error: La imagen '{image_path}' no se encontró.")
        return
    except Exception as e:
        print(f"Error al abrir la imagen '{image_path}': {e}")
        return

    # Normalizar la cantidad de efecto a un rango manejable (e.g., 0-1)
    normalized_effect = effect_amount / 100.0

    # 1. Desenfoque Gaussiano
    blur_radius = 2 + (normalized_effect * 8)
    img_blurred = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    # 2. Superposición de capas con desplazamiento (simulando luces movidas)
    num_layers = int(2 + (normalized_effect * 8))
    max_offset = int(5 + (normalized_effect * 20))

    result_img = np.array(img_blurred, dtype=np.float32)

    for i in range(num_layers):
        offset_x = int(max_offset * (i / (num_layers - 1) - 0.5) * 2)
        offset_y = int(max_offset * (i / (num_layers - 1) - 0.5) * 2)

        shifted_img = Image.new("RGB", img.size)
        shifted_img.paste(img, (offset_x, offset_y))

        alpha = 0.3 - (normalized_effect * 0.2)
        result_img = result_img * (1 - alpha) + np.array(shifted_img, dtype=np.float32) * alpha

    result_img = Image.fromarray(np.uint8(np.clip(result_img, 0, 255)))

    # 3. Adición de grano/ruido
    # La intensidad del ruido ahora es la desviación estándar del ruido gaussiano
    # Reducimos el valor máximo para evitar el "quemado" de píxeles
    noise_intensity = 2 + (normalized_effect * 8)  # De 2 a 10 (antes era hasta 20)

    # Generar ruido como flotante y luego sumarlo, clipear y convertir a uint8
    noise = np.random.normal(0, noise_intensity, (img.height, img.width, 3))
    noisy_img_array = np.array(result_img,
                               dtype=np.float32) + noise  # Aseguramos que result_img sea float32 para la suma
    final_img = Image.fromarray(np.uint8(np.clip(noisy_img_array, 0, 255)))  # Clipear y convertir al final

    # Guardar la imagen
    original_filename = os.path.basename(image_path)
    name, ext = os.path.splitext(original_filename)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filename = f"{name}_{effect_amount}.{output_format.lower()}"
    output_path = os.path.join(output_dir, output_filename)

    save_params = {}
    if output_format.lower() == 'jpg':
        save_params['quality'] = quality
        save_params['optimize'] = True
    elif output_format.lower() == 'webp':
        save_params['quality'] = quality
        save_params['method'] = 6

    try:
        final_img.save(output_path, **save_params)
        print(f"Imagen procesada guardada en: {output_path}")
    except Exception as e:
        print(f"Error al guardar la imagen '{output_path}': {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Aplica un efecto de 'luces movidas' a una imagen o a todas las imágenes en un directorio.")
    parser.add_argument("input_path", help="Ruta a la imagen o directorio de entrada.")
    parser.add_argument("-o", "--output_dir", default="processed_images",
                        help="Directorio para guardar las imágenes procesadas. Por defecto: 'processed_images'.")
    parser.add_argument("-e", "--effect_amount", type=int, default=50,
                        help="Cantidad del efecto a aplicar (0-100). 0 para mínimo, 100 para máximo. Por defecto: 50 (moderado).")
    parser.add_argument("-f", "--format", default="jpg", choices=["jpg", "png", "webp"],
                        help="Formato de salida de la imagen (jpg, png, webp). Por defecto: jpg.")
    parser.add_argument("-q", "--quality", type=int, default=90,
                        help="Calidad de salida para JPG y WebP (0-100). Por defecto: 90.")

    args = parser.parse_args()

    if not 0 <= args.effect_amount <= 100:
        print("Error: La cantidad de efecto debe estar entre 0 y 100.")
        return
    if not 0 <= args.quality <= 100 and args.format in ["jpg", "webp"]:
        print("Error: La calidad debe estar entre 0 y 100.")
        return

    if os.path.isfile(args.input_path):
        apply_light_trail_effect(args.input_path, args.output_dir, args.effect_amount, args.format, args.quality)
    elif os.path.isdir(args.input_path):
        print(f"Procesando imágenes en el directorio: {args.input_path}")
        for filename in os.listdir(args.input_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff')):
                full_path = os.path.join(args.input_path, filename)
                apply_light_trail_effect(full_path, args.output_dir, args.effect_amount, args.format, args.quality)
    else:
        print(f"Error: La ruta de entrada '{args.input_path}' no es un archivo ni un directorio válido.")


if __name__ == "__main__":
    main()