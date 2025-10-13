# PyxelArt - Herramientas de Procesamiento Retro

Una suite modernizada de herramientas para crear efectos retro en imágenes y videos con una arquitectura modular y sin duplicación de código.

## 🚀 Instalación Rápida

### Usando UV (Recomendado)
```bash
# Instalar UV si no lo tienes
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clonar e instalar
git clone <repo>
cd pyxelart
uv venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### Usando pip tradicional
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Scripts de instalación automática
```bash
# Linux/macOS
./install.sh

# Windows
.\install.ps1
```

## 🛠️ Herramientas Principales

### 1. CLI Unificado - `unified_cli.py` ⭐
**La herramienta principal que combina múltiples efectos**

```bash
# Efecto pixel art básico
python unified_cli.py imagen.jpg --effects pixelart --colors 16 --pixel-size 4

# Múltiples efectos combinados
python unified_cli.py imagen.jpg --effects pixelart chromatic dialog --colors 8 --aberration-intensity 1.5

# Aplicar efectos a video
python unified_cli.py video.mp4 --effects pixelart --colors 16 --fps 24 --aspect-ratio 4:3

# Con relación de aspecto personalizada
python unified_cli.py imagen.jpg --effects pixelart --aspect-ratio 1:1 --aspect-method crop
```

### 2. Procesador de Pixel Art - `pyxelart_refactored.py`
**Para efectos de pixel art especializados**

```bash
# Imagen individual
python pyxelart_refactored.py single imagen.jpg --colors 16 --pixel-size 4 --quality 95

# Con diálogo retro
python pyxelart_refactored.py single imagen.jpg --dialog --text "GAME OVER" --colors 8

# Procesamiento por lotes
python pyxelart_refactored.py batch carpeta_imagenes/ --output-dir salida/ --format webp --overwrite

# Con relación de aspecto 4:3 estilo retro
python pyxelart_refactored.py single imagen.jpg --aspect-ratio 4:3 --aspect-method resize --colors 16
```

### 3. Aberración Cromática - `chromatic_aberration_refactored.py`
**Para efectos de aberración cromática específicos**

```bash
# Aberración básica
python chromatic_aberration_refactored.py single imagen.jpg --aberration-intensity 1.5

# Con efecto de lente
python chromatic_aberration_refactored.py single imagen.jpg --aberration-intensity 2.0 --lens-effect

# Desplazamientos personalizados
python chromatic_aberration_refactored.py single imagen.jpg --red-shift 3 0 --blue-shift -3 0 --green-shift 0 1

# Procesamiento por lotes con alta intensidad
python chromatic_aberration_refactored.py batch carpeta/ --output-dir salida/ --aberration-intensity 3.0
```

### 4. Procesador de Video - `video_processor_refactored.py`
**Para efectos retro en videos**

```bash
# Video con efecto pixel art
python video_processor_refactored.py single video.mp4 --colors 16 --pixel-size 6 --fps 24

# Cambiar relación de aspecto a 4:3 retro
python video_processor_refactored.py single video.mp4 --aspect-ratio 4:3 --video-quality 20 --preset fast

# Procesamiento por lotes de videos
python video_processor_refactored.py batch carpeta_videos/ --output-dir videos_retro/ --colors 8 --pixel-size 8
```

## 📋 Guía de Parámetros

### Efectos Disponibles
- `pixelart` - Efecto principal de pixel art con reducción de colores y pixelado
- `chromatic` - Aberración cromática con desplazamiento de canales RGB
- `noise` - Ruido gaussiano para textura retro
- `dialog` - Cuadro de diálogo estilo retro

### Parámetros Comunes

#### Pixel Art
```bash
--colors 16              # Número de colores (4, 8, 16, 32, 64...)
--pixel-size 4           # Tamaño del pixelado (1-20)
--no-noise               # Desactivar ruido
--noise-intensity 15     # Intensidad del ruido (1-50)
```

#### Relación de Aspecto
```bash
--aspect-ratio 4:3       # original, 4:3, 1:1, 16:9
--aspect-method resize   # resize, crop, pad
```

#### Calidad y Formato
```bash
--quality 95             # Calidad de salida (1-100)
--format webp            # png, jpg, webp, mp4, avi
--optimize-web           # Optimizar para web
```

#### Aberración Cromática
```bash
--aberration-intensity 1.5  # Intensidad general (0.1-5.0)
--red-shift 2 0             # Desplazamiento canal rojo (x y)
--green-shift 0 0           # Desplazamiento canal verde (x y)
--blue-shift -2 0           # Desplazamiento canal azul (x y)
--lens-effect               # Activar distorsión de lente
```

#### Video
```bash
--fps 24                 # FPS objetivo
--video-quality 23       # Calidad CRF (0-51, menor = mejor)
--preset medium          # ultrafast, fast, medium, slow, veryslow
```

#### Diálogo Retro
```bash
--dialog                 # Activar cuadro de diálogo
--text "GAME OVER"       # Texto del diálogo
```

## 🎯 Ejemplos Prácticos

### Crear Sprites de Videojuego
```bash
# Convertir personaje a sprite retro 16 colores
python pyxelart_refactored.py single personaje.png --colors 16 --pixel-size 2 --aspect-ratio 1:1 --format png

# Múltiples personajes
python pyxelart_refactored.py batch personajes/ --output-dir sprites/ --colors 16 --pixel-size 2 --format png
```

### Efectos de Pantalla CRT
```bash
# Simular monitor CRT con aberración cromática
python unified_cli.py imagen.jpg --effects pixelart chromatic --colors 64 --pixel-size 2 --aberration-intensity 1.0 --aspect-ratio 4:3
```

### Video Estilo Retro
```bash
# Convertir video moderno a estilo 8-bit
python video_processor_refactored.py single video_moderno.mp4 --colors 8 --pixel-size 6 --fps 15 --aspect-ratio 4:3 --preset fast
```

### Efectos de Juego Retro
```bash
# Pantalla de game over
python unified_cli.py captura.jpg --effects pixelart dialog --colors 4 --pixel-size 8 --dialog --text "GAME OVER" --aspect-ratio 4:3

# Efecto de daño/error en pantalla
python chromatic_aberration_refactored.py single pantalla.jpg --aberration-intensity 3.0 --lens-effect --red-shift 5 0 --blue-shift -5 0
```

### Procesamiento por Lotes Completo
```bash
# Procesar toda una carpeta de imágenes con efecto completo
python unified_cli.py --mode batch carpeta_original/ --output-dir retro_procesado/ --effects pixelart chromatic --colors 16 --aberration-intensity 1.2 --format webp --quality 90 --overwrite
```

## 🔧 Uso Avanzado

### Combinando Herramientas
```bash
# 1. Aplicar pixel art
python pyxelart_refactored.py single imagen.jpg --output paso1.png --colors 16

# 2. Agregar aberración cromática
python chromatic_aberration_refactored.py single paso1.png --output final.png --aberration-intensity 1.5

# O todo en uno:
python unified_cli.py imagen.jpg --effects pixelart chromatic --colors 16 --aberration-intensity 1.5
```

### Para Desarrollo de Juegos
```bash
# Crear tileset retro
python pyxelart_refactored.py batch tiles_originales/ --output-dir tileset_retro/ --colors 16 --pixel-size 1 --format png

# Procesar UI elements
python unified_cli.py ui_modern/ --mode batch --output-dir ui_retro/ --effects pixelart --colors 8 --aspect-ratio 1:1
```

### Para Contenido Social Media
```bash
# Instagram (1:1)
python unified_cli.py foto.jpg --effects pixelart --colors 32 --aspect-ratio 1:1 --aspect-method crop --format jpg --quality 95

# TikTok/YouTube Shorts (9:16)
python unified_cli.py video.mp4 --effects pixelart --colors 16 --aspect-ratio 9:16 --fps 30 --video-quality 20
```

## 🚨 Troubleshooting

### FFmpeg requerido para videos
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Descargar desde https://ffmpeg.org/download.html
```

### Problemas de memoria
```bash
# Reducir calidad para archivos grandes
python unified_cli.py video_grande.mp4 --video-quality 30 --preset ultrafast

# Procesar imágenes en lotes más pequeños
python pyxelart_refactored.py batch carpeta_pequeña/ --colors 8 --pixel-size 4
```

### Archivos muy grandes
```bash
# Optimizar para web
python unified_cli.py imagen_grande.jpg --effects pixelart --format webp --quality 80 --optimize-web
```

## 📁 Estructura del Proyecto

```
pyxelart/
├── utils/                     # Módulos compartidos
│   ├── effects_core.py        # Efectos visuales
│   ├── format_utils.py        # Manejo de formatos
│   ├── file_utils.py          # Procesamiento de archivos
│   ├── cli_utils.py           # Utilidades CLI
│   ├── aspect_ratio_utils.py  # Transformaciones de aspecto
│   └── ffmpeg_utils.py        # Operaciones FFmpeg
├── unified_cli.py             # CLI unificado (PRINCIPAL)
├── pyxelart_refactored.py     # Procesador pixel art
├── chromatic_aberration_refactored.py  # Aberración cromática
├── video_processor_refactored.py       # Procesador de video
├── test/                      # Imágenes de prueba
├── legacy/                    # Herramientas antiguas (preservadas)
└── requirements.txt           # Dependencias
```

## 🎨 Galería de Efectos

### Pixel Art (colors=16, pixel-size=4)
- Reducción a 16 colores
- Pixelado x4
- Ruido retro sutil

### Aberración Cromática (intensity=1.5)
- Desplazamiento RGB
- Efecto de monitor CRT
- Distorsión de lente opcional

### Combinación Completa
- Pixel art + aberración cromática + diálogo
- Aspecto 4:3 clásico
- Optimización de formato

## 🆕 ¿Qué cambió?

### ✅ Eliminada duplicación de código
- **500+ líneas duplicadas** → **150 líneas** de utilidades
- **75% menos código repetido**
- **API consistente** en todas las herramientas

### ✅ Arquitectura modular
- Efectos centralizados en `utils/effects_core.py`
- Manejo unificado de formatos
- CLI reutilizable

### ✅ Herramientas simplificadas
- **`unified_cli.py`** - Una herramienta para múltiples efectos
- Herramientas especializadas más focalizadas
- Mejor rendimiento y mantenibilidad

### ✅ Compatibilidad preservada
- Las herramientas originales están en `legacy/`
- Misma funcionalidad, mejor código
- Migración opcional y gradual

---

**¡Empieza con `unified_cli.py` para la mayoría de casos de uso!**