#!/usr/bin/env python3
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import argparse
import os
from pathlib import Path
from tqdm import tqdm

def apply_aspect_ratio(img, target_ratio, method='resize'):
    """
    Aplica una relación de aspecto específica a la imagen
    
    Args:
        img: La imagen PIL a procesar
        target_ratio: La relación de aspecto objetivo (ancho/alto), por ejemplo 4/3 o 1/1
        method: 'resize' para estirar la imagen, 'crop' para recortar
        
    Returns:
        La imagen PIL con la nueva relación de aspecto
    """
    width, height = img.size
    current_ratio = width / height
    
    if abs(current_ratio - target_ratio) < 0.01:
        # Ya tiene la relación de aspecto correcta
        return img
    
    if method == 'resize':
        # Calcular nuevas dimensiones manteniendo la altura
        new_width = int(height * target_ratio)
        return img.resize((new_width, height), Image.LANCZOS)
    
    elif method == 'crop':
        if current_ratio > target_ratio:
            # Imagen más ancha que lo deseado, recortar los lados
            new_w = int(height * target_ratio)
            # Centrar el recorte
            x_offset = (width - new_w) // 2
            return img.crop((x_offset, 0, x_offset + new_w, height))
        else:
            # Imagen más alta que lo deseado, recortar arriba y abajo
            new_h = int(width / target_ratio)
            # Centrar el recorte
            y_offset = (height - new_h) // 2
            return img.crop((0, y_offset, width, y_offset + new_h))
    
    return img

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

def retro_effect(input_path, output_path=None, width=None, height=None, color_depth=16, 
                 pixel_size=4, add_dialog=False, dialog_text="", 
                 aspect_ratio=None, aspect_method='resize', quality=95, output_format=None):
    """
    Aplica un efecto retro a una imagen individual
    
    Args:
        input_path: Ruta de la imagen de entrada
        output_path: Ruta de la imagen de salida (opcional)
        width: Ancho de salida (opcional)
        height: Alto de salida (opcional)
        color_depth: Número de colores (por defecto: 16)
        pixel_size: Tamaño de pixelado (por defecto: 4)
        add_dialog: Añadir cuadro de diálogo (por defecto: False)
        dialog_text: Texto para el cuadro de diálogo (por defecto: "")
        aspect_ratio: Relación de aspecto de salida (por defecto: None)
        aspect_method: Método para ajustar relación de aspecto ('resize' o 'crop')
        quality: Calidad de la imagen para formatos con compresión (1-100, por defecto: 95)
        output_format: Formato de salida ('png', 'jpg', 'webp', o None para usar original)
    """
    # Cargar imagen
    img = Image.open(input_path)
    
    # Detectar si la imagen tiene canal alfa (transparencia)
    has_alpha = img.mode == 'RGBA' or 'A' in img.getbands()
    
    # Aplicar relación de aspecto si se especifica
    if aspect_ratio is not None:
        img = apply_aspect_ratio(img, aspect_ratio, aspect_method)
    
    # Redimensionar si se especifica
    if width and height:
        img = img.resize((width, height), Image.LANCZOS)
    
    # Aplicar reducción de colores preservando canal alfa si existe
    if has_alpha:
        # Separar canales RGB y Alpha
        rgb = img.convert('RGB')
        alpha = img.split()[-1]
        
        # Reducir colores en RGB
        rgb = rgb.convert('P', palette=Image.ADAPTIVE, colors=color_depth)
        rgb = rgb.convert('RGB')
        
        # Pixelado a RGB
        pixel_width = rgb.width // pixel_size
        pixel_height = rgb.height // pixel_size
        rgb = rgb.resize((pixel_width, pixel_height), Image.NEAREST)
        rgb = rgb.resize((rgb.width * pixel_size, rgb.height * pixel_size), Image.NEAREST)
        
        # Pixelado al canal alpha
        alpha = alpha.resize((pixel_width, pixel_height), Image.NEAREST)
        alpha = alpha.resize((rgb.width, rgb.height), Image.NEAREST)
        
        # Aplicar ruido solo a canales RGB
        np_rgb = np.array(rgb)
        noise = np.random.randint(0, 15, np_rgb.shape)
        np_rgb = np.clip(np_rgb + noise, 0, 255).astype(np.uint8)
        rgb_with_noise = Image.fromarray(np_rgb)
        
        # Recombinar RGB y Alpha
        final_img = rgb_with_noise.convert('RGBA')
        final_img.putalpha(alpha)
    else:
        # Aplicar reducción de colores
        img = img.convert('P', palette=Image.ADAPTIVE, colors=color_depth)
        img = img.convert('RGB')
        
        # Pixelado
        pixel_width = img.width // pixel_size
        pixel_height = img.height // pixel_size
        img = img.resize((pixel_width, pixel_height), Image.NEAREST)
        img = img.resize((img.width * pixel_size, img.height * pixel_size), Image.NEAREST)
        
        # Aplicar ruido/dithering para estética retro
        np_img = np.array(img)
        noise = np.random.randint(0, 15, np_img.shape)
        np_img = np.clip(np_img + noise, 0, 255).astype(np.uint8)
        
        final_img = Image.fromarray(np_img)
    
    # Opcional: añadir cuadro de diálogo estilo retro
    if add_dialog and dialog_text:
        # Crear nuevo canvas con o sin alpha según corresponda
        if has_alpha:
            dialog_height = pixel_size * 10
            canvas = Image.new('RGBA', (final_img.width, final_img.height + dialog_height), (50, 50, 50, 255))
            canvas.paste(final_img, (0, 0), final_img if has_alpha else None)
        else:
            dialog_height = pixel_size * 10
            canvas = Image.new('RGB', (final_img.width, final_img.height + dialog_height), (50, 50, 50))
            canvas.paste(final_img, (0, 0))
        
        draw = ImageDraw.Draw(canvas)
        dialog_box = (10, final_img.height + 5, final_img.width - 10, final_img.height + dialog_height - 5)
        draw.rectangle(dialog_box, fill=(80, 80, 80), outline=(200, 200, 200))
        
        try:
            font = ImageFont.truetype("arial.ttf", pixel_size * 3)
        except:
            font = ImageFont.load_default()
            
        text_pos = (dialog_box[0] + 10, dialog_box[1] + 10)
        draw.text(text_pos, dialog_text, fill=(0, 0, 200), font=font)
        
        final_img = canvas
    
    # Configuración de salida por defecto si no se especifica
    if not output_path:
        filename, ext = os.path.splitext(input_path)
        # Usar formato especificado o mantener el original
        if output_format:
            ext = f".{output_format}"
        output_path = f"{filename}_retro-c{color_depth}-p{pixel_size}{ext}"
    else:
        # Si se especifica output_path y output_format, asegurar la extensión correcta
        if output_format:
            output_path = str(Path(output_path).with_suffix(f".{output_format}"))
    
    # Determinar opciones de guardado según el formato
    save_options = {}
    lower_path = output_path.lower()
    
    # Aplicar calidad para formatos que la soportan
    if lower_path.endswith('.jpg') or lower_path.endswith('.jpeg'):
        save_options['quality'] = quality
        save_options['format'] = 'JPEG'
        save_options['optimize'] = True
    elif lower_path.endswith('.png'):
        save_options['format'] = 'PNG'
        save_options['optimize'] = True
        compression_level = min(9, max(0, 9 - int(quality / 11)))
        save_options['compress_level'] = compression_level
    elif lower_path.endswith('.webp'):
        save_options['quality'] = quality
        save_options['format'] = 'WEBP'
        save_options['lossless'] = False
        if has_alpha:
            save_options['exact'] = True
    
    # Si la imagen tiene alpha pero el formato no lo soporta, convertir a RGB
    if has_alpha and not (lower_path.endswith('.png') or lower_path.endswith('.webp')):
        print(f"Aviso: Se perderá la transparencia al guardar en formato {Path(output_path).suffix}")
        final_img = final_img.convert('RGB')
    
    final_img.save(output_path, **save_options)
    
    print(f"Imagen procesada guardada en: {output_path}")
    return final_img

def process_image_directory(input_dir, output_dir=None, width=None, height=None, 
                           color_depth=16, pixel_size=4, add_dialog=False, dialog_text="",
                           aspect_ratio=None, aspect_method='resize', quality=95, output_format=None):
    """
    Procesa todas las imágenes en un directorio
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
    
    # Extensiones de imágenes a procesar
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp']
    
    # Buscar todas las imágenes en el directorio
    images = [f for f in input_path.iterdir() 
              if f.is_file() and f.suffix.lower() in image_extensions]
    
    if not images:
        print(f"No se encontraron imágenes en {input_dir}")
        return
    
    print(f"Encontradas {len(images)} imágenes para procesar")
    
    # Procesar cada imagen
    for i, file_path in enumerate(images, 1):
        # Determinar extensión de salida
        if output_format:
            output_extension = f".{output_format}"
        else:
            output_extension = file_path.suffix
        
        output_file = output_path / f"{file_path.stem}_retro-c{color_depth}-p{pixel_size}{output_extension}"
        
        print(f"Procesando imagen {i}/{len(images)}: {file_path.name}")
        
        # Procesar la imagen
        retro_effect(
            str(file_path), str(output_file), width, height, 
            color_depth, pixel_size, add_dialog, dialog_text,
            aspect_ratio, aspect_method, quality, output_format
        )
    
    print(f"\nProceso completo: {len(images)} imágenes convertidas")
    print(f"Resultados guardados en: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Aplicar efecto retro a imágenes')
    
    # Crear subparsers para los diferentes modos
    subparsers = parser.add_subparsers(dest='mode', help='Modo de operación')
    
    # Subparser para procesamiento individual
    parser_single = subparsers.add_parser('single', help='Procesar una sola imagen')
    parser_single.add_argument('input', help='Ruta de la imagen de entrada')
    parser_single.add_argument('--output', help='Ruta para guardar la imagen procesada')
    parser_single.add_argument('--width', type=int, help='Ancho de salida')
    parser_single.add_argument('--height', type=int, help='Alto de salida')
    parser_single.add_argument('--colors', type=int, default=16, help='Profundidad de color')
    parser_single.add_argument('--pixel-size', type=int, default=4, help='Tamaño de pixelado')
    parser_single.add_argument('--dialog', action='store_true', help='Añadir cuadro de diálogo')
    parser_single.add_argument('--text', default='', help='Texto para el cuadro de diálogo')
    parser_single.add_argument('--aspect-ratio', choices=['4:3', '1:1', 'original'], default='original',
                               help='Relación de aspecto de la imagen de salida')
    parser_single.add_argument('--aspect-method', choices=['resize', 'crop'], default='resize',
                               help='Método para ajustar la relación de aspecto')
    parser_single.add_argument('--quality', type=int, default=95, 
                               help='Calidad de la imagen para formatos con compresión (1-100, mayor es mejor)')
    parser_single.add_argument('--format', choices=['png', 'jpg', 'webp'], 
                               help='Formato de salida (default: mantener formato original)')
    
    # Subparser para procesamiento por lotes
    parser_batch = subparsers.add_parser('batch', help='Procesar múltiples imágenes en un directorio')
    parser_batch.add_argument('input_dir', help='Directorio con las imágenes a procesar')
    parser_batch.add_argument('--output-dir', help='Directorio donde guardar las imágenes procesadas')
    parser_batch.add_argument('--width', type=int, help='Ancho de salida')
    parser_batch.add_argument('--height', type=int, help='Alto de salida')
    parser_batch.add_argument('--colors', type=int, default=16, help='Profundidad de color')
    parser_batch.add_argument('--pixel-size', type=int, default=4, help='Tamaño de pixelado')
    parser_batch.add_argument('--dialog', action='store_true', help='Añadir cuadro de diálogo')
    parser_batch.add_argument('--text', default='', help='Texto para el cuadro de diálogo')
    parser_batch.add_argument('--aspect-ratio', choices=['4:3', '1:1', 'original'], default='original',
                             help='Relación de aspecto de las imágenes de salida')
    parser_batch.add_argument('--aspect-method', choices=['resize', 'crop'], default='resize',
                             help='Método para ajustar la relación de aspecto')
    parser_batch.add_argument('--quality', type=int, default=95, 
                             help='Calidad de la imagen para formatos con compresión (1-100, mayor es mejor)')
    parser_batch.add_argument('--format', choices=['png', 'jpg', 'webp'], 
                             help='Formato de salida (default: mantener formato original)')
    
    args = parser.parse_args()
    
    try:
        # Convertir aspect_ratio a valor numérico
        aspect_ratio_value = None
        if hasattr(args, 'aspect_ratio'):
            aspect_ratio_value = parse_aspect_ratio(args.aspect_ratio)
        
        if args.mode == 'single':
            retro_effect(
                args.input, args.output, args.width, args.height, 
                args.colors, args.pixel_size, args.dialog, args.text,
                aspect_ratio_value, args.aspect_method, args.quality, args.format
            )
        elif args.mode == 'batch':
            process_image_directory(
                args.input_dir, args.output_dir, args.width, args.height,
                args.colors, args.pixel_size, args.dialog, args.text,
                aspect_ratio_value, args.aspect_method, args.quality, args.format
            )
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")