# Sprite Cutter

Una herramienta de línea de comandos para recortar sprites de animación para videojuegos, desarrollada en Python.

## Características

- ✂️ Recorta una imagen o un directorio completo de imágenes en frames individuales
- 🔄 Soporte para división horizontal y vertical
- 🧠 Detección automática de zonas transparentes
- 📏 Especificación flexible de dimensiones (ancho o ancho×alto)
- 🎯 Opciones para añadir padding y redimensionar frames
- 🖼️ Múltiples formatos de salida (PNG, WebP, GIF) con control de calidad
- 📁 Organización automática en carpetas con nombres en minúsculas

## Requisitos

- Python 3.6 o superior
- Pillow (PIL Fork)
- NumPy

## Instalación

1. Clona o descarga este repositorio
2. Instala las dependencias:

```bash
pip install pillow numpy
```

## Uso

```bash
python sprite_cutter.py [opciones] imagen_o_directorio
```

### Opciones

| Opción | Descripción |
|--------|-------------|
| `--width WIDTH` | Ancho de cada frame (o WIDTHxHEIGHT para especificar también el alto) |
| `--slices NUMBER` | Número de divisiones a realizar |
| `--direction {h,v}` | Dirección de corte (h=horizontal, v=vertical) [por defecto: h] |
| `--output-dir DIR` | Directorio donde guardar los resultados |
| `--format {png,webp,gif}` | Formato de salida [por defecto: png] |
| `--quality QUALITY` | Calidad de la imagen (1-100) [por defecto: 90] |
| `--padding PADDING` | Padding a añadir alrededor de cada frame [por defecto: 0] |
| `--resize RESIZE` | Redimensionar frames (WIDTHxHEIGHT) [opcional] |
| `--no-auto-detect` | Desactivar la detección automática de zonas transparentes |

## Ejemplos

### Recortar una imagen en frames de 48 píxeles de ancho
```bash
python sprite_cutter.py ruta/a/sprite.png --width 48
```

### Recortar con alto y ancho específicos
```bash
python sprite_cutter.py ruta/a/sprite.png --width 48x64
```

### Recortar un directorio completo en 8 divisiones
```bash
python sprite_cutter.py ruta/a/sprites/ --slices 8
```

### Recortar verticalmente
```bash
python sprite_cutter.py ruta/a/sprite.png --width 48 --direction v
```

### Añadir padding y guardar en formato WebP con calidad específica
```bash
python sprite_cutter.py ruta/a/sprite.png --width 48 --padding 2 --format webp --quality 85
```

### Desactivar la detección automática
```bash
python sprite_cutter.py ruta/a/sprite.png --width 48 --no-auto-detect
```

### Redimensionar los frames
```bash
python sprite_cutter.py ruta/a/sprite.png --width 48 --resize 32x32
```

## Funcionamiento

### Detección de zonas transparentes

Por defecto, el script detecta automáticamente las regiones no transparentes de la imagen para optimizar el recorte. Esto es especialmente útil cuando los sprites no están perfectamente alineados o tienen espacios vacíos entre ellos.

- En modo horizontal: detecta columnas verticales con píxeles no transparentes
- En modo vertical: detecta filas horizontales con píxeles no transparentes

Si prefieres divisiones exactas según el ancho especificado, puedes desactivar esta función con `--no-auto-detect`.

### Estructura de salida

Para cada imagen procesada, el script crea:

1. Un directorio con el nombre de la imagen en minúsculas (sin extensión)
2. Archivos de frame dentro del directorio con el formato: `[nombre_imagen]_[número].png`

Por ejemplo, si procesas `Run.png`, obtendrás:
```
run/
  ├── run_1.png
  ├── run_2.png
  ├── run_3.png
  └── ...
```

## Trucos y consejos

- Para spritesets complejos, la detección automática funciona mejor
- Para hojas de sprites uniformes, usar `--no-auto-detect` con `--width` puede dar resultados más predecibles
- Añadir un pequeño padding (`--padding 1` o `--padding 2`) puede ayudar a evitar artefactos en los bordes
- Para mantener la máxima calidad, usa PNG como formato de salida
- Para optimizar el tamaño de archivo, usa WebP con una calidad adecuada (70-85)

## Cómo funciona

El script utiliza la biblioteca Pillow (PIL) para la manipulación de imágenes y NumPy para la detección eficiente de regiones transparentes. El proceso de recorte sigue estos pasos:

1. Carga la imagen de entrada
2. Determina las dimensiones de corte según los parámetros
3. Si la detección automática está habilitada, analiza la imagen para encontrar regiones no transparentes
4. Recorta la imagen en frames individuales
5. Aplica padding y/o redimensionamiento si se especifica
6. Guarda los frames en el formato solicitado

## Limitaciones conocidas

- La detección automática funciona mejor con imágenes que tienen fondo transparente
- Para GIFs animados, el script trata la imagen como un solo frame (no extrae los frames de animación del GIF)
- No admite la recombinación de frames en una animación (solo divide, no une)

## Licencia

Este software se distribuye bajo la licencia MIT.