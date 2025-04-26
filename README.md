# Actualizaciones a los scripts de PyxelArt

## Nuevas funcionalidades

Se han actualizado los scripts con las siguientes mejoras:

1. **Estructura unificada** con comandos `single` y `batch`:
   - Todos los scripts ahora usan subcomandos para procesar archivos individuales o en lotes
   - La sintaxis es consistente entre los diferentes scripts

2. **Soporte para cambiar la relación de aspecto**:
   - Opciones para cambiar a relación 4:3 o 1:1
   - Dos métodos disponibles: redimensionado (`resize`) o recorte (`crop`)

## Comandos actualizados

### pyxelart.py (para imágenes)

```bash
# Procesar imagen individual
python pyxelart.py single imagen.jpg --colors 16 --pixel-size 4

# Procesar imagen con relación de aspecto 4:3
python pyxelart.py single imagen.jpg --aspect-ratio 4:3 --aspect-method resize

# Procesar imagen con relación de aspecto 1:1 recortando
python pyxelart.py single imagen.jpg --aspect-ratio 1:1 --aspect-method crop

# Procesar lote de imágenes
python pyxelart.py batch carpeta_imagenes --colors 16 --pixel-size 4

# Procesar lote de imágenes con relación de aspecto 4:3
python pyxelart.py batch carpeta_imagenes --aspect-ratio 4:3
```

### pyxelart_gif.py (video a GIF)

```bash
# Procesar video individual
python pyxelart_gif.py single video.mp4 --colors 16 --pixel-size 4

# Procesar video con relación de aspecto 4:3
python pyxelart_gif.py single video.mp4 --aspect-ratio 4:3 --aspect-method resize

# Procesar video con relación de aspecto 1:1 recortando
python pyxelart_gif.py single video.mp4 --aspect-ratio 1:1 --aspect-method crop

# Procesar lote de videos
python pyxelart_gif.py batch carpeta_videos --colors 16 --pixel-size 4

# Procesar lote de videos con relación de aspecto 4:3
python pyxelart_gif.py batch carpeta_videos --aspect-ratio 4:3
```

### pyxelart_video.py (video a video con audio)

```bash
# Procesar video individual
python pyxelart_video.py single video.mp4 --colors 16 --pixel-size 4

# Procesar video con relación de aspecto 4:3
python pyxelart_video.py single video.mp4 --aspect-ratio 4:3 --aspect-method resize

# Procesar video con relación de aspecto 1:1 recortando
python pyxelart_video.py single video.mp4 --aspect-ratio 1:1 --aspect-method crop

# Procesar lote de videos
python pyxelart_video.py batch carpeta_videos --colors 16 --pixel-size 4

# Procesar lote de videos con relación de aspecto 4:3
python pyxelart_video.py batch carpeta_videos --aspect-ratio 4:3
```

## Parámetros de relación de aspecto

| Parámetro | Descripción | Opciones |
|-----------|-------------|----------|
| `--aspect-ratio` | Relación de aspecto deseada | `4:3`, `1:1`, `original` |
| `--aspect-method` | Método para aplicar la relación | `resize` (estirar/comprimir), `crop` (recortar) |

### Métodos de ajuste:

- **resize**: Estira o comprime la imagen para ajustarla a la proporción deseada
- **crop**: Recorta los bordes de la imagen para lograr la proporción deseada (mantiene el centro)

## Notas

- El método `resize` puede distorsionar la imagen, pero no pierde contenido
- El método `crop` mantiene las proporciones originales, pero recorta partes de la imagen
- Si la imagen/video ya tiene la relación solicitada, no se realiza ningún cambio