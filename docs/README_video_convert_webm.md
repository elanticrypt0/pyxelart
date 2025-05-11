# WebM Converter

Un módulo de Python para convertir videos a formato WebM con opciones de control de calidad, redimensionamiento y recorte. Compatible con procesamiento de archivos individuales o por lotes.

## Características

- Conversión de videos a formato WebM usando el códec VP9
- Preservación del audio original (usando el códec Opus)
- Control de calidad personalizable (0-100)
- Opciones para redimensionar videos
- Posibilidad de recortar videos
- Procesamiento por lotes de directorios completos
- Soporte para procesamiento recursivo de subdirectorios
- Procesamiento en paralelo para mejorar el rendimiento

## Requisitos

- Python 3.6+
- FFmpeg instalado en el sistema

## Instalación

1. Asegúrate de tener FFmpeg instalado:
   - **Linux**: `sudo apt-get install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Descarga desde [ffmpeg.org](https://ffmpeg.org/download.html)

2. Coloca el archivo `webm_converter.py` en tu proyecto

## Uso

### Como script de línea de comandos

#### Convertir un archivo individual:

```bash
python webm_converter.py file input_video.mp4 --quality 75 --resize 1280x720
```

#### Convertir todos los videos en un directorio:

```bash
python webm_converter.py dir /ruta/videos --output-dir /ruta/salida --quality 60 --recursive
```

### Parámetros

#### Modos

- `file`: Procesa un archivo individual
- `dir`: Procesa todos los videos en un directorio

#### Argumentos comunes

- `--quality`: Calidad del video (0-100, default: 50)
- `--resize`: Redimensionar video (formato: widthxheight)
- `--crop`: Recortar video (formato: x:y:width:height)

#### Modo archivo

- `input`: Ruta del archivo de video de entrada
- `--output`: Ruta del archivo de salida (opcional)

#### Modo directorio

- `input_dir`: Directorio con los videos de entrada
- `--output-dir`: Directorio para guardar los videos convertidos (opcional)
- `--recursive`: Buscar videos en subdirectorios
- `--workers`: Número máximo de trabajos en paralelo

## Ejemplos

### Convertir un video a calidad máxima:

```bash
python webm_converter.py file input_video.mp4 --quality 100
```

### Convertir y redimensionar un video:

```bash
python webm_converter.py file input_video.mp4 --resize 1920x1080
```

### Recortar un video:

```bash
python webm_converter.py file input_video.mp4 --crop 100:50:1280:720
```

### Procesar todos los videos en un directorio:

```bash
python webm_converter.py dir /ruta/videos
```

### Procesar videos recursivamente con 4 workers:

```bash
python webm_converter.py dir /ruta/videos --recursive --workers 4
```

## Como módulo

También puedes importar las funciones y utilizarlas en tu propio código:

```python
from webm_converter import convert_to_webm, process_directory

# Convertir un archivo
convert_to_webm('input.mp4', 'output.webm', quality=75, resize=(1280, 720))

# Procesar un directorio
process_directory('/ruta/videos', '/ruta/salida', quality=60, recursive=True)
```

## Formatos de entrada soportados

- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- FLV (.flv)
- WMV (.wmv)
- WebM (.webm)