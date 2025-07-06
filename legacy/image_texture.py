# Corrección en image_texture.py
import argparse
import os
from PIL import Image, ImageFilter
import numpy as np

def apply_texture_effect(image_path, output_dir, effect_amount, output_format='tiff', quality=90):
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

    # 1. Reducción de detalles finos (desenfoque ligero)
    blur_radius = 1 + (normalized_effect * 2)
    img_blurred = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    # 2. Adición de grano/ruido sutil
    # Reducimos la intensidad máxima del ruido para que sea más sutil
    noise_intensity = 2 + (normalized_effect * 5) # De 2 a 7 (antes era hasta 15)

    # Generar ruido como flotante y luego sumarlo, clipear y convertir a uint8
    noise = np.random.normal(0, noise_intensity, (img.height, img.width, 3))
    noisy_img_array = np.array(img_blurred, dtype=np.float32) + noise
    img_with_noise = Image.fromarray(np.uint8(np.clip(noisy_img_array, 0, 255)))

    # 3. Superposición de textura de lienzo simulada
    def generate_fractal_noise(size, scale=8.0, octaves=6, persistence=0.5, lacunarity=2.0):
        shape_for_noise_gen = (size[1], size[0])

        def fbm_2d(shape, base_frequency, frequencies, amplitudes):
            grid = np.mgrid[tuple(slice(0, dim, 1j * num) for dim, num in zip(shape, shape))]
            sample = np.zeros(shape)
            for i in range(len(frequencies)):
                frequency = frequencies[i]
                amplitude = amplitudes[i]
                sample += amplitude * np.sin(np.pi * base_frequency * frequency * grid).prod(0)
            return sample

        frequencies = [scale * (lacunarity ** i) for i in range(octaves)]
        amplitudes = [persistence ** i for i in range(octaves)]
        noise = fbm_2d(shape_for_noise_gen, 1.0, frequencies, amplitudes)
        return (noise + 1) / 2

    fractal_noise = generate_fractal_noise(img.size)
    noise_img = Image.fromarray(np.uint8(fractal_noise * 255)).convert("L")

    texture_opacity = 0.1 + (normalized_effect * 0.2)
    # Blend con la imagen que ya tiene el ruido gaussiano
    final_img = Image.blend(img_with_noise, noise_img.convert("RGB"), texture_opacity)


    # Guardar la imagen
    original_filename = os.path.basename(image_path)
    name, ext = os.path.splitext(original_filename)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filename = f"{name}_textured_{effect_amount}.{output_format.lower()}"
    output_path = os.path.join(output_dir, output_filename)

    save_params = {}
    if output_format.lower() == 'jpg':
        save_params['quality'] = quality
        save_params['optimize'] = True
    elif output_format.lower() == 'webp':
        save_params['quality'] = quality
        save_params['method'] = 6
    elif output_format.lower() == 'tiff':
         save_params['compression'] = 'lzw'

    try:
        final_img.save(output_path, **save_params)
        print(f"Imagen procesada guardada en: {output_path}")
    except Exception as e:
        print(f"Error al guardar la imagen '{output_path}': {e}")


def main():
    parser = argparse.ArgumentParser(description="Aplica un efecto de 'textura pictórica' a una imagen o a todas las imágenes en un directorio.")
    parser.add_argument("input_path", help="Ruta a la imagen o directorio de entrada.")
    parser.add_argument("-o", "--output_dir", default="processed_images", help="Directorio para guardar las imágenes procesadas. Por defecto: 'processed_images'.")
    parser.add_argument("-e", "--effect_amount", type=int, default=50,
                        help="Cantidad del efecto de textura a aplicar (0-100). 0 para mínimo, 100 para máximo. Por defecto: 50 (moderado).")
    parser.add_argument("-f", "--format", default="tiff", choices=["jpg", "png", "webp", "tiff"],
                        help="Formato de salida de la imagen (jpg, png, webp, tiff). Por defecto: tiff.")
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
        apply_texture_effect(args.input_path, args.output_dir, args.effect_amount, args.format, args.quality)
    elif os.path.isdir(args.input_path):
        print(f"Procesando imágenes en el directorio: {args.input_path}")
        for filename in os.listdir(args.input_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff')):
                full_path = os.path.join(args.input_path, filename)
                apply_texture_effect(full_path, args.output_dir, args.effect_amount, args.format, args.quality)
    else:
        print(f"Error: La ruta de entrada '{args.input_path}' no es un archivo ni un directorio válido.")


if __name__ == "__main__":
    main()