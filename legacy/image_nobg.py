#!/usr/bin/env python3
import numpy as np
from PIL import Image
import argparse
import os
from pathlib import Path
from tqdm import tqdm
import cv2
import imageio
import tempfile
from rembg import remove, new_session

def process_image(input_path, output_path=None, model="u2net", alpha_matting=False, 
                  alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10,
                  alpha_matting_erode_size=10, quality=95, output_format="png"):
    """
    Remueve el fondo de una imagen individual
    
    Args:
        input_path: Ruta de la imagen de entrada
        output_path: Ruta de la imagen de salida (opcional)
        model: Modelo a utilizar para la segmentación ('u2net', 'u2netp', 'u2net_human_seg', etc.)
        alpha_matting: Usar alpha matting para mejorar bordes (más lento)
        alpha_matting_foreground_threshold: Umbral para el primer plano en alpha matting (0-255)
        alpha_matting_background_threshold: Umbral para el fondo en alpha matting (0-255)
        alpha_matting_erode_size: Tamaño de erosión para alpha matting
        quality: Calidad para formatos con compresión (0-100, mayor es mejor)
        output_format: Formato de salida ('png', 'webp', 'tiff')
    """
    # Configuración de salida por defecto si no se especifica
    if not output_path:
        filename, ext = os.path.splitext(input_path)
        output_path = f"{filename}_nobg.{output_format}"
    else:
        # Asegurar que la extensión coincida con el formato especificado
        output_base = os.path.splitext(output_path)[0]
        output_path = f"{output_base}.{output_format}"
    
    print(f"Procesando imagen: {os.path.basename(input_path)}")
    
    # Cargar imagen
    img = Image.open(input_path)
    
    # Crear una sesión con el modelo especificado
    session = new_session(model)
    
    # Remover fondo
    result = remove(
        img, 
        session=session,
        alpha_matting=alpha_matting,
        alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
        alpha_matting_background_threshold=alpha_matting_background_threshold,
        alpha_matting_erode_size=alpha_matting_erode_size
    )
    
    # Determinar el formato de salida y configurar opciones
    save_options = {}
    
    if output_format == 'png':
        # Para PNG, calidad se convierte en nivel de compresión (0-9)
        compression_level = min(9, max(0, 9 - int(quality / 11)))
        save_options = {
            'format': 'PNG',
            'compress_level': compression_level,
            'optimize': True
        }
    elif output_format == 'webp':
        # WebP soporta calidad directamente
        save_options = {
            'format': 'WEBP',
            'quality': quality,
            'method': 6,  # Método de compresión (0-6), mayor es mejor pero más lento
            'lossless': False,
            'exact': True  # Preservar transparencia exacta
        }
    elif output_format in ['tiff', 'tif']:
        # TIFF tiene diferentes opciones de compresión
        save_options = {
            'format': 'TIFF',
            'compression': 'tiff_lzw'  # Otras opciones: 'tiff_deflate', 'tiff_adobe_deflate', etc.
        }
    
    # Guardar resultado con las opciones configuradas
    result.save(output_path, **save_options)
    
    print(f"Imagen procesada guardada en: {output_path}")
    return result

def process_image_directory(input_dir, output_dir=None, model="u2net", alpha_matting=False, 
                           alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10,
                           alpha_matting_erode_size=10, quality=95, output_format="png"):
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
        output_path = input_path / "nobg"
    
    output_path.mkdir(exist_ok=True)
    
    # Extensiones de imágenes a procesar
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    
    # Buscar todas las imágenes en el directorio
    images = [f for f in input_path.iterdir() 
              if f.is_file() and f.suffix.lower() in image_extensions]
    
    if not images:
        print(f"No se encontraron imágenes en {input_dir}")
        return
    
    print(f"Encontradas {len(images)} imágenes para procesar")
    
    # Crear sesión con el modelo especificado para reutilizarla
    session = new_session(model)
    
    # Procesar cada imagen
    for i, file_path in enumerate(tqdm(images, desc="Procesando imágenes")):
        output_file = output_path / f"{file_path.stem}_nobg.{output_format}"
        
        # Cargar imagen
        img = Image.open(file_path)
        
        # Remover fondo
        result = remove(
            img, 
            session=session,
            alpha_matting=alpha_matting,
            alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
            alpha_matting_background_threshold=alpha_matting_background_threshold,
            alpha_matting_erode_size=alpha_matting_erode_size
        )
        
        # Guardar resultado con las opciones configuradas según el formato
        save_options = {}
        
        if output_format == 'png':
            compression_level = min(9, max(0, 9 - int(quality / 11)))
            save_options = {
                'format': 'PNG',
                'compress_level': compression_level,
                'optimize': True
            }
        elif output_format == 'webp':
            save_options = {
                'format': 'WEBP',
                'quality': quality,
                'method': 6,
                'lossless': False,
                'exact': True
            }
        
        result.save(output_file, **save_options)
    
    print(f"\nProceso completo: {len(images)} imágenes procesadas")
    print(f"Resultados guardados en: {output_path}")

def process_gif(input_path, output_path=None, model="u2net", alpha_matting=False, 
               alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10,
               alpha_matting_erode_size=10, quality=95):
    """
    Remueve el fondo de un archivo GIF
    """
    # Configuración de salida por defecto si no se especifica
    if not output_path:
        filename, _ = os.path.splitext(input_path)
        output_path = f"{filename}_nobg.gif"
    
    print(f"Procesando GIF: {os.path.basename(input_path)}")
    
    # Cargar el GIF
    gif = Image.open(input_path)
    
    # Verificar que es un GIF animado
    if not getattr(gif, "is_animated", False):
        print("El archivo no es un GIF animado. Procesando como imagen estática...")
        result = process_image(input_path, output_path, model, alpha_matting,
                             alpha_matting_foreground_threshold, alpha_matting_background_threshold,
                             alpha_matting_erode_size, quality)
        return output_path
    
    # Obtener información del GIF original
    n_frames = gif.n_frames
    duration = gif.info.get('duration', 100)  # Duración de cada frame en ms
    
    print(f"GIF tiene {n_frames} frames")
    
    # Crear sesión con el modelo especificado para reutilizarla
    session = new_session(model)
    
    # Lista para almacenar frames procesados
    processed_frames = []
    
    # Procesar cada frame
    for i in tqdm(range(n_frames), desc="Procesando frames"):
        gif.seek(i)
        frame = gif.convert("RGBA")
        
        # Remover fondo del frame
        frame_no_bg = remove(
            frame,
            session=session,
            alpha_matting=alpha_matting,
            alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
            alpha_matting_background_threshold=alpha_matting_background_threshold,
            alpha_matting_erode_size=alpha_matting_erode_size
        )
        
        # Añadir a la lista de frames procesados
        processed_frames.append(frame_no_bg)
    
    # Guardar el GIF resultante con la calidad configurada
    # Nota: GIF tiene limitaciones de color, así que utiliza una paleta adaptativa
    processed_frames[0].save(
        output_path,
        save_all=True,
        append_images=processed_frames[1:],
        optimize=True,  # Optimizar para reducir tamaño
        duration=duration,
        loop=0,
        disposal=2,  # Modo de disposición para transparencias
        quality=quality  # Afecta a la cuantización de colores en GIF
    )
    
    print(f"GIF procesado guardado en: {output_path}")
    return output_path

def process_gif_directory(input_dir, output_dir=None, model="u2net", alpha_matting=False, 
                         alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10,
                         alpha_matting_erode_size=10, quality=95):
    """
    Procesa todos los GIFs en un directorio
    """
    # Asegurar que el directorio existe
    input_path = Path(input_dir)
    if not input_path.exists() or not input_path.is_dir():
        raise ValueError(f"El directorio {input_dir} no existe")
    
    # Crear directorio de salida
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = input_path / "nobg"
    
    output_path.mkdir(exist_ok=True)
    
    # Extensiones de GIFs a procesar
    gif_extensions = ['.gif']
    
    # Buscar todos los GIFs en el directorio
    gifs = [f for f in input_path.iterdir() 
            if f.is_file() and f.suffix.lower() in gif_extensions]
    
    if not gifs:
        print(f"No se encontraron GIFs en {input_dir}")
        return
    
    print(f"Encontrados {len(gifs)} GIFs para procesar")
    
    # Procesar cada GIF
    for i, file_path in enumerate(gifs, 1):
        # Ruta de salida
        output_file = output_path / f"{file_path.stem}_nobg{file_path.suffix}"
        
        print(f"\nProcesando GIF {i}/{len(gifs)}: {file_path.name}")
        
        # Procesar el GIF
        process_gif(
            str(file_path), str(output_file), model, alpha_matting,
            alpha_matting_foreground_threshold, alpha_matting_background_threshold,
            alpha_matting_erode_size, quality
        )
    
    print(f"\nProceso completo: {len(gifs)} GIFs procesados")
    print(f"Resultados guardados en: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Remover fondo de imágenes y GIFs')
    
    # Crear subparsers para los diferentes modos
    subparsers = parser.add_subparsers(dest='mode', help='Modo de operación')
    
    # Subparser para procesamiento de imagen individual
    parser_image = subparsers.add_parser('image', help='Procesar una sola imagen')
    parser_image.add_argument('input', help='Ruta de la imagen de entrada')
    parser_image.add_argument('--output', help='Ruta para guardar la imagen procesada')
    parser_image.add_argument('--model', choices=['u2net', 'u2netp', 'u2net_human_seg', 'silueta'], 
                             default='u2net_human_seg', 
                             help='Modelo a utilizar (u2net_human_seg recomendado para personas)')
    parser_image.add_argument('--alpha-matting', action='store_true', 
                             help='Usar alpha matting para mejorar los bordes (más lento)')
    parser_image.add_argument('--foreground-threshold', type=int, default=240, 
                             help='Umbral para el primer plano en alpha matting (0-255)')
    parser_image.add_argument('--background-threshold', type=int, default=10, 
                             help='Umbral para el fondo en alpha matting (0-255)')
    parser_image.add_argument('--erode-size', type=int, default=10, 
                             help='Tamaño de erosión para alpha matting')
    parser_image.add_argument('--quality', type=int, default=95, 
                             help='Calidad de la imagen para formatos con compresión (1-100, mayor es mejor)')
    parser_image.add_argument('--format', choices=['png', 'webp', 'tiff'], default='png',
                             help='Formato de salida (default: png)')
    
    # Subparser para procesamiento de directorio de imágenes
    parser_image_dir = subparsers.add_parser('images', help='Procesar múltiples imágenes en un directorio')
    parser_image_dir.add_argument('input_dir', help='Directorio con las imágenes a procesar')
    parser_image_dir.add_argument('--output-dir', help='Directorio donde guardar las imágenes procesadas')
    parser_image_dir.add_argument('--model', choices=['u2net', 'u2netp', 'u2net_human_seg', 'silueta'], 
                                default='u2net_human_seg', 
                                help='Modelo a utilizar (u2net_human_seg recomendado para personas)')
    parser_image_dir.add_argument('--alpha-matting', action='store_true', 
                                help='Usar alpha matting para mejorar los bordes (más lento)')
    parser_image_dir.add_argument('--foreground-threshold', type=int, default=240, 
                                help='Umbral para el primer plano en alpha matting (0-255)')
    parser_image_dir.add_argument('--background-threshold', type=int, default=10, 
                                help='Umbral para el fondo en alpha matting (0-255)')
    parser_image_dir.add_argument('--erode-size', type=int, default=10, 
                                help='Tamaño de erosión para alpha matting')
    parser_image_dir.add_argument('--quality', type=int, default=95, 
                                help='Calidad de la imagen para formatos con compresión (1-100, mayor es mejor)')
    parser_image_dir.add_argument('--format', choices=['png', 'webp', 'tiff'], default='png',
                                help='Formato de salida (default: png)')
    
    # Subparser para procesamiento de GIF individual
    parser_gif = subparsers.add_parser('gif', help='Procesar un solo GIF')
    parser_gif.add_argument('input', help='Ruta del GIF de entrada')
    parser_gif.add_argument('--output', help='Ruta para guardar el GIF procesado')
    parser_gif.add_argument('--model', choices=['u2net', 'u2netp', 'u2net_human_seg', 'silueta'], 
                          default='u2net_human_seg', 
                          help='Modelo a utilizar (u2net_human_seg recomendado para personas)')
    parser_gif.add_argument('--alpha-matting', action='store_true', 
                          help='Usar alpha matting para mejorar los bordes (más lento)')
    parser_gif.add_argument('--foreground-threshold', type=int, default=240, 
                          help='Umbral para el primer plano en alpha matting (0-255)')
    parser_gif.add_argument('--background-threshold', type=int, default=10, 
                          help='Umbral para el fondo en alpha matting (0-255)')
    parser_gif.add_argument('--erode-size', type=int, default=10, 
                          help='Tamaño de erosión para alpha matting')
    parser_gif.add_argument('--quality', type=int, default=95, 
                          help='Calidad para GIF (1-100, afecta a la cuantización de colores)')
    
    # Subparser para procesamiento de directorio de GIFs
    parser_gif_dir = subparsers.add_parser('gifs', help='Procesar múltiples GIFs en un directorio')
    parser_gif_dir.add_argument('input_dir', help='Directorio con los GIFs a procesar')
    parser_gif_dir.add_argument('--output-dir', help='Directorio donde guardar los GIFs procesados')
    parser_gif_dir.add_argument('--model', choices=['u2net', 'u2netp', 'u2net_human_seg', 'silueta'], 
                              default='u2net_human_seg', 
                              help='Modelo a utilizar (u2net_human_seg recomendado para personas)')
    parser_gif_dir.add_argument('--alpha-matting', action='store_true', 
                              help='Usar alpha matting para mejorar los bordes (más lento)')
    parser_gif_dir.add_argument('--foreground-threshold', type=int, default=240, 
                              help='Umbral para el primer plano en alpha matting (0-255)')
    parser_gif_dir.add_argument('--background-threshold', type=int, default=10, 
                              help='Umbral para el fondo en alpha matting (0-255)')
    parser_gif_dir.add_argument('--erode-size', type=int, default=10, 
                              help='Tamaño de erosión para alpha matting')
    parser_gif_dir.add_argument('--quality', type=int, default=95, 
                              help='Calidad para GIF (1-100, afecta a la cuantización de colores)')
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'image':
            process_image(
                args.input, args.output, args.model, args.alpha_matting,
                args.foreground_threshold, args.background_threshold, args.erode_size,
                args.quality, args.format
            )
        elif args.mode == 'images':
            process_image_directory(
                args.input_dir, args.output_dir, args.model, args.alpha_matting,
                args.foreground_threshold, args.background_threshold, args.erode_size,
                args.quality, args.format
            )
        elif args.mode == 'gif':
            process_gif(
                args.input, args.output, args.model, args.alpha_matting,
                args.foreground_threshold, args.background_threshold, args.erode_size,
                args.quality
            )
        elif args.mode == 'gifs':
            process_gif_directory(
                args.input_dir, args.output_dir, args.model, args.alpha_matting,
                args.foreground_threshold, args.background_threshold, args.erode_size,
                args.quality
            )
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")