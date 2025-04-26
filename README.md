# PyxelArt

Herramienta Python para transformar imágenes y videos modernos en gráficos estilo retro con efectos de videojuegos clásicos.

## Características

- Pixelado configurable
- Reducción de paleta de colores
- Efecto de ruido/dithering
- Adición opcional de cuadros de diálogo estilo aventura gráfica
- Redimensionado personalizable
- Soporte para cambio de relación de aspecto (4:3, 1:1)
- Procesamiento de imágenes a imágenes
- Conversión de video a GIF animado
- Conversión de video a video con efectos retro (preservando audio)
- Control de calidad y tamaño para videos
- Procesamiento por lotes de múltiples archivos

## Requisitos

- Python 3.6+
- Pillow
- NumPy
- OpenCV (cv2)
- imageio
- tqdm
- FFmpeg (opcional, para preservar audio en videos)

## Instalación

### 1. Crear un entorno virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
# Con pip
pip install -r requirements.txt

# Con uv (más rápido)
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 3. Instalar FFmpeg (para preservar audio en videos)

**Windows:**
- Descargar de [ffmpeg.org](https://ffmpeg.org/download.html)
- Extraer y añadir la carpeta bin al PATH del sistema

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update && sudo apt install ffmpeg  # Ubuntu/Debian
sudo dnf install ffmpeg                     # Fedora
sudo pacman -S ffmpeg                       # Arch Linux
```

## Uso

### Imágenes (pyxelart.py)

```bash
# Procesar una imagen individual
python pyxelart.py single imagen.jpg

# Opciones adicionales
python pyxelart.py single imagen.jpg --output salida.png --width 320 --height 240 --colors 16 --pixel-size 4 --dialog --text "Texto de ejemplo" --aspect-ratio 4:3 --aspect-method resize

# Procesar múltiples imágenes
python pyxelart.py batch carpeta_imagenes --colors 8 --pixel-size 6
```

### Video a GIF (pyxelart_gif.py)

```bash
# Convertir un video a GIF
python pyxelart_gif.py single video.mp4

# Opciones adicionales
python pyxelart_gif.py single video.mp4 --output animacion.gif --width 320 --height 240 --colors 16 --pixel-size 4 --frame-skip 2 --fps 10 --dialog --text "Texto animado" --aspect-ratio 1:1 --aspect-method crop

# Procesar múltiples videos
python pyxelart_gif.py batch carpeta_videos --colors 16 --fps 12
```

### Video a Video (pyxelart_video.py)

```bash
# Procesar un video manteniendo el formato
python pyxelart_video.py single video.mp4

# Opciones adicionales
python pyxelart_video.py single video.mp4 --output video_retro.mp4 --width 640 --height 480 --colors 8 --pixel-size 6 --frame-skip 2 --dialog --text "Texto retro" --format .mp4 --aspect-ratio 4:3 --aspect-method resize --quality 20 --preset medium

# Procesar múltiples videos
python pyxelart_video.py batch carpeta_videos --colors 16 --quality 23
```

## Argumentos comunes

| Argumento | Descripción | Por defecto |
|-----------|-------------|-------------|
| `--output` | Ruta de salida | *nombre_original*_retro-c{color_depth}-p{pixel_size}.*extensión* |
| `--width` | Ancho de salida | (original) |
| `--height` | Alto de salida | (original) |
| `--colors` | Profundidad de color | 16 |
| `--pixel-size` | Nivel de pixelado | 4 |
| `--dialog` | Incluir cuadro de diálogo | False |
| `--text` | Texto para el cuadro de diálogo | "" |
| `--aspect-ratio` | Relación de aspecto | "original" (también: "4:3", "1:1") |
| `--aspect-method` | Método para ajustar aspecto | "resize" (también: "crop") |

## Argumentos específicos para GIF (pyxelart_gif.py)

| Argumento | Descripción | Por defecto |
|-----------|-------------|-------------|
| `--frame-skip` | Saltar N frames entre capturas | 2 |
| `--fps` | Frames por segundo del GIF | 10 |

## Argumentos específicos para Video (pyxelart_video.py)

| Argumento | Descripción | Por defecto |
|-----------|-------------|-------------|
| `--frame-skip` | Saltar N frames entre capturas | 1 |
| `--fps` | Frames por segundo | (original) |
| `--format` | Formato del video de salida | .mp4 (también: .avi, .mov, .mkv) |
| `--quality` | Calidad de compresión (1-51) | 23 (menor = mejor calidad) |
| `--preset` | Preset de codificación | medium |

## Control de calidad para videos

### Valores recomendados para calidad (--quality)

| Calidad Deseada | Valor CRF | Tamaño Resultante |
|-----------------|-----------|-------------------|
| Alta calidad (casi sin pérdida) | 17-18 | ~60-70% del original |
| Buena calidad (equilibrada) | 19-23 | ~40-50% del original |
| Calidad media (ahorro espacio) | 24-28 | ~25-35% del original |
| Calidad baja (máximo ahorro) | 29-35 | ~15-20% del original |

### Presets de codificación (--preset)

* **ultrafast**: Mayor velocidad, peor compresión (archivos más grandes)
* **veryfast/faster**: Buena velocidad, compresión razonable
* **medium**: Equilibrio predeterminado
* **slow/slower**: Mejor compresión, menor velocidad
* **veryslow**: Máxima compresión, velocidad muy lenta

## Relación de aspecto

### Métodos de ajuste:

- **resize**: Estira o comprime la imagen para ajustarla a la proporción deseada
- **crop**: Recorta los bordes de la imagen para lograr la proporción deseada (mantiene el centro)

## Ejemplos de uso

### Imágenes
- Crear estilo de aventura gráfica de los 90s:
  ```bash
  python pyxelart.py single foto.jpg --colors 16 --pixel-size 4 --dialog --text "She's doing things to you alright, look at those... Legs"
  ```

- Estilo 8-bit con alta pixelación:
  ```bash
  python pyxelart.py single foto.jpg --colors 8 --pixel-size 8
  ```

- Imagen para formato Instagram (1:1):
  ```bash
  python pyxelart.py single foto.jpg --aspect-ratio 1:1 --aspect-method crop
  ```

### Videos a GIF
- Convertir video a GIF con estilo de 16 colores:
  ```bash
  python pyxelart_gif.py single video.mp4 --colors 16 --pixel-size 4
  ```

- GIF de baja calidad pero más rápido de generar:
  ```bash
  python pyxelart_gif.py single video.mp4 --frame-skip 5 --fps 8
  ```

- Clip estilo 4:3 con texto en la parte inferior:
  ```bash
  python pyxelart_gif.py single video.mp4 --aspect-ratio 4:3 --dialog --text "Again your searching for..."
  ```

### Videos a Videos Retro
- Video con calidad alta y buena compresión:
  ```bash
  python pyxelart_video.py single video.mp4 --quality 18 --preset medium
  ```

- Video con estilo de 8 colores y máximo ahorro de espacio:
  ```bash
  python pyxelart_video.py single video.mp4 --colors 8 --quality 28 --preset slow
  ```

- Convertir video a AVI con relación 4:3:
  ```bash
  python pyxelart_video.py single video.mp4 --format .avi --aspect-ratio 4:3 --dialog --text "Press SPACE to continue..."
  ```

- Procesamiento rápido para pruebas:
  ```bash
  python pyxelart_video.py single video.mp4 --quality 23 --preset veryfast
  ```

### Procesamiento por lotes
- Convertir todas las imágenes de una carpeta:
  ```bash
  python pyxelart.py batch carpeta_con_fotos
  ```

- Procesar múltiples videos y convertirlos a GIFs:
  ```bash
  python pyxelart_gif.py batch videos/ --colors 16 --fps 10
  ```

- Procesar múltiples videos con compresión óptima:
  ```bash
  python pyxelart_video.py batch carpeta_videos --quality 20 --preset slow
  ```

## Notas

- La carpeta de salida para procesamiento por lotes es `./retro` junto a la carpeta original
- El método `resize` puede distorsionar la imagen, pero no pierde contenido
- El método `crop` mantiene las proporciones originales, pero recorta partes de la imagen
- FFmpeg es necesario para preservar audio en videos procesados
- Para videos, valores de calidad menores producen mejor calidad visual pero archivos más grandes

## Licencia

MIT