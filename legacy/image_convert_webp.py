#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
from PIL import Image
from tqdm import tqdm

def convert_to_webp(input_path, output_path=None, quality=80, lossless=False):
    """
    Convierte una imagen a formato WebP
    
    Args:
        input_path: Ruta de la imagen de entrada
        output_path: Ruta de la imagen de salida (opcional)
        quality: Calidad de compresión (1-100, por defecto: 80)
        lossless: Si True, usa compresión sin pérdida (por defecto: False)
    
    Returns:
        Path: Ruta del archivo de salida
    """
    try:
        # Abrir imagen
        img = Image.open(input_path)
        
        # Detectar si la imagen tiene transparencia
        has_alpha = img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)
        
        # Manejar GIFs animados
        if hasattr(img, 'is_animated') and img.is_animated:
            print(f"Advertencia: {input_path} es un GIF animado. Solo se convertirá el primer frame.")
            img.seek(0)
        
        # Si es un GIF con transparencia, convertir a RGBA
        if img.mode == 'P' and 'transparency' in img.info:
            img = img.convert('RGBA')
        
        # Configurar ruta de salida
        if output_path is None:
            output_path = Path(input_path).with_suffix('.webp')
        else:
            output_path = Path(output_path)
            # Asegurar que la extensión sea .webp
            if output_path.suffix.lower() != '.webp':
                output_path = output_path.with_suffix('.webp')
        
        # Configurar opciones de guardado
        save_options = {
            'format': 'WEBP',
            'quality': quality,
            'lossless': lossless,
            'method': 6  # Mejor compresión (más lento)
        }
        
        # Preservar transparencia si existe
        if has_alpha:
            save_options['exact'] = True
            if not lossless:
                save_options['alpha_quality'] = quality
        
        # Guardar imagen
        img.save(str(output_path), **save_options)
        
        # Información sobre el archivo
        original_size = os.path.getsize(input_path)
        new_size = os.path.getsize(output_path)
        reduction = ((original_size - new_size) / original_size) * 100
        
        print(f"Convertido: {input_path}")
        print(f"  → {output_path}")
        print(f"  Tamaño original: {original_size / 1024:.1f} KB")
        print(f"  Tamaño nuevo: {new_size / 1024:.1f} KB")
        print(f"  Reducción: {reduction:.1f}%")
        
        return output_path
        
    except Exception as e:
        print(f"Error al convertir {input_path}: {e}")
        return None

def process_directory(input_dir, output_dir=None, quality=80, lossless=False, recursive=False):
    """
    Procesa todas las imágenes en un directorio
    
    Args:
        input_dir: Directorio de entrada
        output_dir: Directorio de salida (opcional)
        quality: Calidad de compresión (1-100)
        lossless: Si True, usa compresión sin pérdida
        recursive: Si True, procesa subdirectorios recursivamente
    
    Returns:
        int: Número de archivos procesados exitosamente
    """
    input_path = Path(input_dir)
    if not input_path.exists() or not input_path.is_dir():
        raise ValueError(f"El directorio {input_dir} no existe")
    
    # Configurar directorio de salida
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = input_path
    
    # Extensiones de imagen soportadas
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif'}
    
    # Recolectar archivos a procesar
    if recursive:
        image_files = []
        for ext in image_extensions:
            image_files.extend(input_path.rglob(f'*{ext}'))
            image_files.extend(input_path.rglob(f'*{ext.upper()}'))
    else:
        image_files = []
        for ext in image_extensions:
            image_files.extend(input_path.glob(f'*{ext}'))
            image_files.extend(input_path.glob(f'*{ext.upper()}'))
    
    # Eliminar duplicados y ordenar
    image_files = sorted(set(image_files))
    
    if not image_files:
        print(f"No se encontraron imágenes en {input_dir}")
        return 0
    
    successful_conversions = 0
    
    print(f"Encontrados {len(image_files)} archivos para convertir")
    
    # Procesar cada archivo
    for image_file in tqdm(image_files, desc="Convirtiendo imágenes"):
        # Calcular ruta de salida manteniendo estructura de directorios si es recursivo
        if recursive and output_dir:
            relative_path = image_file.relative_to(input_path)
            output_file = output_path / relative_path.with_suffix('.webp')
            output_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            output_file = output_path / image_file.with_suffix('.webp').name
        
        if convert_to_webp(str(image_file), str(output_file), quality, lossless):
            successful_conversions += 1
    
    print(f"\nConversión completa: {successful_conversions}/{len(image_files)} archivos convertidos exitosamente")
    return successful_conversions

def main():
    parser = argparse.ArgumentParser(description='Convertir imágenes a formato WebP')
    
    subparsers = parser.add_subparsers(dest='mode', help='Modo de operación', required=True)
    
    # Subparser para archivos individuales
    parser_single = subparsers.add_parser('single', help='Convertir un archivo individual')
    parser_single.add_argument('input', help='Archivo de entrada')
    parser_single.add_argument('-o', '--output', help='Archivo de salida (opcional)')
    parser_single.add_argument('-q', '--quality', type=int, default=80,
                             help='Calidad de compresión (1-100, default: 80)')
    parser_single.add_argument('--lossless', action='store_true',
                             help='Usar compresión sin pérdida')
    
    # Subparser para procesamiento por lotes
    parser_batch = subparsers.add_parser('batch', help='Convertir múltiples archivos en un directorio')
    parser_batch.add_argument('input_dir', help='Directorio de entrada')
    parser_batch.add_argument('-o', '--output-dir', help='Directorio de salida (opcional)')
    parser_batch.add_argument('-q', '--quality', type=int, default=80,
                            help='Calidad de compresión (1-100, default: 80)')
    parser_batch.add_argument('--lossless', action='store_true',
                            help='Usar compresión sin pérdida')
    parser_batch.add_argument('-r', '--recursive', action='store_true',
                            help='Procesar subdirectorios recursivamente')
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'single':
            # Validar calidad
            if not 1 <= args.quality <= 100:
                raise ValueError("La calidad debe estar entre 1 y 100")
            
            convert_to_webp(args.input, args.output, args.quality, args.lossless)
            
        elif args.mode == 'batch':
            # Validar calidad
            if not 1 <= args.quality <= 100:
                raise ValueError("La calidad debe estar entre 1 y 100")
            
            process_directory(args.input_dir, args.output_dir, args.quality, 
                            args.lossless, args.recursive)
    
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()