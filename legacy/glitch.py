# -*- coding: utf-8 -*-
import os
import random
from PIL import Image, ImageChops, ImageFilter, ImageEnhance
import argparse


# --- Funciones de Efectos ---

def apply_chromatic_aberration(image, offset_r=(5, 0), offset_g=(0, 0), offset_b=(-5, 0)):
    """
    Aplica un efecto de aberración cromática a la imagen.
    Desplaza ligeramente los canales Rojo, Verde y Azul.

    Args:
        image (PIL.Image.Image): La imagen de entrada.
        offset_r (tuple): Desplazamiento (x, y) para el canal Rojo.
        offset_g (tuple): Desplazamiento (x, y) para el canal Verde.
        offset_b (tuple): Desplazamiento (x, y) para el canal Azul.

    Returns:
        PIL.Image.Image: La imagen con aberración cromática.
    """
    if image.mode != 'RGB' and image.mode != 'RGBA':
        image = image.convert('RGB')  # Asegurarse de que sea RGB para separar canales

    r, g, b = image.split()[:3]  # Ignorar alpha si existe para la aberración

    r = ImageChops.offset(r, offset_r[0], offset_r[1])
    g = ImageChops.offset(g, offset_g[0], offset_g[1])
    b = ImageChops.offset(b, offset_b[0], offset_b[1])

    # Si la imagen original tenía canal alfa, lo reincorporamos
    if image.mode == 'RGBA':
        alpha = image.split()[3]
        return Image.merge('RGBA', (r, g, b, alpha))
    else:
        return Image.merge('RGB', (r, g, b))


def apply_glitch_blocks(image, intensity=10, block_size_min=10, block_size_max=50, seed=None):
    """
    Aplica un efecto de glitch moviendo bloques aleatorios de la imagen.

    Args:
        image (PIL.Image.Image): La imagen de entrada.
        intensity (int): Número de bloques a desplazar.
        block_size_min (int): Tamaño mínimo del lado del bloque.
        block_size_max (int): Tamaño máximo del lado del bloque.
        seed (int, optional): Semilla para el generador de números aleatorios.

    Returns:
        PIL.Image.Image: La imagen con el efecto de bloques.
    """
    if seed is not None:
        random.seed(seed)

    img_copy = image.copy()
    width, height = img_copy.size

    for _ in range(intensity):
        # Asegurar que los tamaños de bloque no sean cero
        actual_block_size_min = max(1, block_size_min)
        actual_block_size_max = max(actual_block_size_min, block_size_max)

        block_w = random.randint(actual_block_size_min, actual_block_size_max)
        block_h = random.randint(actual_block_size_min, actual_block_size_max)

        # Coordenadas del bloque original (asegurando que esté dentro de los límites)
        src_x = random.randint(0, max(0, width - block_w))
        src_y = random.randint(0, max(0, height - block_h))

        # Coordenadas del destino del bloque (asegurando que esté dentro de los límites)
        dst_x = random.randint(0, max(0, width - block_w))
        dst_y = random.randint(0, max(0, height - block_h))

        # Evitar extraer una región vacía si el tamaño del bloque es mayor que la imagen
        if block_w > width or block_h > height:
            continue
        if src_x + block_w > width or src_y + block_h > height:
            continue

        box = (src_x, src_y, src_x + block_w, src_y + block_h)
        region = img_copy.crop(box)

        # Aplicar alguna manipulación simple al bloque (opcional)
        # region = region.transpose(Image.FLIP_LEFT_RIGHT)
        # enhancer = ImageEnhance.Brightness(region)
        # region = enhancer.enhance(random.uniform(0.5, 1.5))

        img_copy.paste(region, (dst_x, dst_y))

    return img_copy


def apply_glitch_horizontal_shift(image, intensity=5, shift_height_min=5, shift_height_max=20, max_offset=50,
                                  seed=None):
    """
    Aplica un efecto de glitch desplazando franjas horizontales.

    Args:
        image (PIL.Image.Image): La imagen de entrada.
        intensity (int): Número de franjas a desplazar.
        shift_height_min (int): Altura mínima de la franja.
        shift_height_max (int): Altura máxima de la franja.
        max_offset (int): Desplazamiento horizontal máximo.
        seed (int, optional): Semilla para el generador de números aleatorios.

    Returns:
        PIL.Image.Image: La imagen con el efecto de desplazamiento horizontal.
    """
    if seed is not None:
        random.seed(seed)

    img_copy = image.copy()
    width, height = img_copy.size
    pixels = img_copy.load()  # Usar load() para manipulación más rápida si es necesario, pero crop/paste es más seguro

    for _ in range(intensity):
        # Asegurar que las alturas no sean cero
        actual_shift_height_min = max(1, shift_height_min)
        actual_shift_height_max = max(actual_shift_height_min, shift_height_max)

        strip_height = random.randint(actual_shift_height_min, actual_shift_height_max)

        # Asegurar que y_start esté dentro de los límites
        y_start = random.randint(0, max(0, height - strip_height))

        # Evitar extraer una región vacía
        if strip_height == 0 or y_start + strip_height > height:
            continue

        box = (0, y_start, width, y_start + strip_height)
        strip = img_copy.crop(box)

        offset = random.randint(-max_offset, max_offset)

        # Crear una nueva franja desplazada
        shifted_strip = ImageChops.offset(strip, offset, 0)

        img_copy.paste(shifted_strip, (0, y_start))

    return img_copy


def apply_glitch_scanlines(image, intensity=0.1, line_height=1, line_color=(0, 0, 0, 100), seed=None):
    """
    Aplica un efecto de glitch de líneas de escaneo.

    Args:
        image (PIL.Image.Image): La imagen de entrada.
        intensity (float): Densidad de las líneas (0.0 a 1.0). Afecta la probabilidad de dibujar una línea.
        line_height (int): Grosor de las líneas.
        line_color (tuple): Color RGBA de las líneas.
        seed (int, optional): Semilla para el generador de números aleatorios.

    Returns:
        PIL.Image.Image: La imagen con el efecto de líneas de escaneo.
    """
    if seed is not None:
        random.seed(seed)

    img_copy = image.copy()
    if img_copy.mode != 'RGBA':
        img_copy = img_copy.convert('RGBA')  # Necesitamos RGBA para dibujar líneas con transparencia

    width, height = img_copy.size
    overlay = Image.new('RGBA', img_copy.size, (255, 255, 255, 0))  # Capa transparente para dibujar líneas

    from PIL import ImageDraw  # Importación local para evitar dependencia global si no se usa
    draw = ImageDraw.Draw(overlay)

    for y in range(0, height, line_height * 2):  # Iterar para crear espacios entre líneas
        if random.random() < intensity:
            draw.line([(0, y), (width, y)], fill=line_color, width=line_height)

    # Componer la imagen original con la capa de líneas
    img_with_scanlines = Image.alpha_composite(img_copy, overlay)

    # Si la imagen original no era RGBA, convertir de nuevo si es necesario, o mantener RGBA
    # Por simplicidad, la mantenemos como RGBA ya que el formato de salida lo manejará
    return img_with_scanlines


# --- Función Principal y Manejo de Archivos ---

def process_image(filepath, output_dir, args):
    """
    Carga una imagen, aplica los efectos seleccionados y la guarda.
    """
    try:
        img = Image.open(filepath)
        original_format = img.format
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)

        print(f"Procesando: {filename}...")

        # Aplicar aberración cromática si está habilitada
        if args.chroma_aberration:
            offsets_str = args.chroma_offsets.split(',')
            if len(offsets_str) == 6:  # R_x,R_y,G_x,G_y,B_x,B_y
                try:
                    offset_r = (int(offsets_str[0]), int(offsets_str[1]))
                    offset_g = (int(offsets_str[2]), int(offsets_str[3]))
                    offset_b = (int(offsets_str[4]), int(offsets_str[5]))
                    img = apply_chromatic_aberration(img, offset_r, offset_g, offset_b)
                    print(f"  Aberración cromática aplicada con offsets: R{offset_r}, G{offset_g}, B{offset_b}")
                except ValueError:
                    print(f"  ADVERTENCIA: Formato de chroma_offsets incorrecto. Usando valores por defecto.")
                    img = apply_chromatic_aberration(img)  # Usar por defecto si hay error
            else:
                print(f"  ADVERTENCIA: Se esperaban 6 valores para chroma_offsets. Usando valores por defecto.")
                img = apply_chromatic_aberration(img)  # Usar por defecto

        # Aplicar efecto glitch seleccionado
        if args.glitch_type == "blocks":
            img = apply_glitch_blocks(img, args.glitch_intensity, args.block_size_min, args.block_size_max, args.seed)
            print(f"  Efecto glitch 'blocks' aplicado con intensidad {args.glitch_intensity}.")
        elif args.glitch_type == "h_shift":
            img = apply_glitch_horizontal_shift(img, args.glitch_intensity, args.shift_height_min,
                                                args.shift_height_max, args.shift_max_offset, args.seed)
            print(f"  Efecto glitch 'h_shift' aplicado con intensidad {args.glitch_intensity}.")
        elif args.glitch_type == "scanlines":
            # Convertir color de línea de string a tupla
            try:
                line_color_parts = [int(c.strip()) for c in args.scanline_color.split(',')]
                if len(line_color_parts) == 3:  # RGB
                    scanline_color_rgba = tuple(line_color_parts + [args.scanline_alpha])
                elif len(line_color_parts) == 4:  # RGBA
                    scanline_color_rgba = tuple(line_color_parts)
                else:
                    raise ValueError("Color de línea debe ser R,G,B o R,G,B,A")
            except ValueError as e:
                print(
                    f"  ADVERTENCIA: Color de scanline inválido ('{args.scanline_color}'). Usando negro por defecto. Error: {e}")
                scanline_color_rgba = (0, 0, 0, args.scanline_alpha)  # Negro semitransparente por defecto

            img = apply_glitch_scanlines(img, args.scanline_density, args.scanline_height, scanline_color_rgba,
                                         args.seed)
            print(f"  Efecto glitch 'scanlines' aplicado con densidad {args.scanline_density}.")
        elif args.glitch_type == "none":
            print("  No se aplicó ningún efecto glitch principal.")
            pass  # No aplicar glitch si es 'none'

        # Guardar imagen
        output_format = args.output_format.lower()
        output_filename = f"{name}_glitched.{output_format}"
        output_path = os.path.join(output_dir, output_filename)

        save_params = {}
        if output_format == 'webp':
            save_params['quality'] = args.quality
            save_params['lossless'] = False  # Puedes hacerlo configurable si quieres webp sin pérdida
        elif output_format == 'jpeg' or output_format == 'jpg':
            save_params['quality'] = args.quality
            save_params['optimize'] = True
            # JPEG no soporta transparencia, convertir a RGB si es RGBA
            if img.mode == 'RGBA':
                print("  Convirtiendo a RGB para formato JPEG (elimina transparencia).")
                img = img.convert('RGB')
        elif output_format == 'png':
            save_params['optimize'] = True  # PNG también puede tener compresión/optimización
            # La calidad no es un parámetro directo para PNG como en JPG/WEBP,
            # pero 'optimize' ayuda. Podrías añadir 'compress_level' (0-9) si es necesario.

        img.save(output_path, **save_params)
        print(
            f"  Imagen guardada como: {output_path} (Formato: {output_format.upper()}, Calidad: {args.quality if output_format in ['webp', 'jpeg', 'jpg'] else 'N/A'})")

    except FileNotFoundError:
        print(f"Error: Archivo no encontrado - {filepath}")
    except Exception as e:
        print(f"Error procesando {filepath}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Aplica efectos glitch y aberración cromática a imágenes.")
    parser.add_argument("input_path", help="Ruta a la imagen o directorio de imágenes.")
    parser.add_argument("-o", "--output_dir", default="output_glitched",
                        help="Directorio para guardar las imágenes procesadas (por defecto: output_glitched).")

    # Argumentos para Aberración Cromática
    parser.add_argument("--chroma_aberration", action="store_true", help="Habilitar efecto de aberración cromática.")
    parser.add_argument("--chroma_offsets", type=str, default="5,0,0,0,-5,0",
                        help="Offsets (x,y) para canales R,G,B. Formato: 'Rx,Ry,Gx,Gy,Bx,By'. Ejemplo: '5,0,0,0,-5,0'")

    # Argumentos para Efectos Glitch
    parser.add_argument("--glitch_type", choices=["blocks", "h_shift", "scanlines", "none"], default="blocks",
                        help="Tipo de efecto glitch a aplicar (por defecto: blocks). 'none' para no aplicar glitch principal.")
    parser.add_argument("--glitch_intensity", type=int, default=20,
                        help="Intensidad general para el glitch (número de bloques/franjas). (por defecto: 20)")

    # Parámetros específicos para 'blocks'
    parser.add_argument("--block_size_min", type=int, default=10,
                        help="Tamaño mínimo del lado del bloque para glitch 'blocks'. (por defecto: 10)")
    parser.add_argument("--block_size_max", type=int, default=70,
                        help="Tamaño máximo del lado del bloque para glitch 'blocks'. (por defecto: 70)")

    # Parámetros específicos para 'h_shift'
    parser.add_argument("--shift_height_min", type=int, default=5,
                        help="Altura mínima de la franja para glitch 'h_shift'. (por defecto: 5)")
    parser.add_argument("--shift_height_max", type=int, default=30,
                        help="Altura máxima de la franja para glitch 'h_shift'. (por defecto: 30)")
    parser.add_argument("--shift_max_offset", type=int, default=60,
                        help="Desplazamiento horizontal máximo para glitch 'h_shift'. (por defecto: 60)")

    # Parámetros específicos para 'scanlines'
    parser.add_argument("--scanline_density", type=float, default=0.15,
                        help="Densidad de las líneas de escaneo (0.0 a 1.0). (por defecto: 0.15)")
    parser.add_argument("--scanline_height", type=int, default=1,
                        help="Grosor de las líneas de escaneo. (por defecto: 1)")
    parser.add_argument("--scanline_color", type=str, default="0,0,0",
                        help="Color RGB de las líneas de escaneo (ej. '255,0,0' para rojo). (por defecto: '0,0,0' - negro)")
    parser.add_argument("--scanline_alpha", type=int, default=100,
                        help="Transparencia (alfa) de las líneas de escaneo (0-255). (por defecto: 100)")

    # Argumentos para Formato de Salida
    parser.add_argument("--output_format", choices=["webp", "jpeg", "jpg", "png"], default="webp",
                        help="Formato de la imagen de salida (por defecto: webp).")
    parser.add_argument("--quality", type=int, default=80, choices=range(1, 101), metavar="[1-100]",
                        help="Calidad para formatos WebP y JPEG (1-100, por defecto: 80).")

    # Semilla para aleatoriedad
    parser.add_argument("--seed", type=int, default=None,
                        help="Semilla para el generador de números aleatorios para reproducibilidad.")

    args = parser.parse_args()

    # Crear directorio de salida si no existe
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        print(f"Directorio de salida creado: {args.output_dir}")

    # Establecer semilla si se proporcionó
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Usando semilla para aleatoriedad: {args.seed}")

    # Procesar imagen(es)
    if os.path.isfile(args.input_path):
        process_image(args.input_path, args.output_dir, args)
    elif os.path.isdir(args.input_path):
        print(f"Procesando directorio: {args.input_path}")
        for item in os.listdir(args.input_path):
            item_path = os.path.join(args.input_path, item)
            # Comprobar si es un archivo y si es una imagen (simple comprobación de extensión)
            if os.path.isfile(item_path) and item.lower().endswith(
                    ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')):
                process_image(item_path, args.output_dir, args)
            else:
                print(f"Omitiendo: {item_path} (no es un archivo de imagen soportado o es un subdirectorio)")
    else:
        print(f"Error: La ruta de entrada '{args.input_path}' no es un archivo ni un directorio válido.")


if __name__ == "__main__":
    main()
