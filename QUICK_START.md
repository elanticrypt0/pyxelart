# 🚀 Guía de Inicio Rápido - PyxelArt

## ⚡ Instalación en 2 minutos

```bash
# 1. Activar entorno
source .venv/bin/activate  # o .venv\Scripts\activate en Windows

# 2. ¡Listo! Ya puedes usar las herramientas
```

## 🎮 Pruebas Rápidas

### Efecto Pixel Art Básico
```bash
python unified_cli.py test/unnamed9.jpg --effects pixelart --colors 16 --pixel-size 4
```

### Estilo Retro Completo
```bash
python unified_cli.py test/unnamed9.jpg --effects pixelart chromatic dialog --colors 8 --text "RETRO GAME" --aspect-ratio 4:3
```

### Para Sprites de Juego
```bash
python pyxelart_refactored.py single test/unnamed9.jpg --colors 16 --pixel-size 2 --aspect-ratio 1:1 --format png
```

### Efecto CRT Monitor
```bash
python chromatic_aberration_refactored.py single test/unnamed9.jpg --aberration-intensity 2.0 --lens-effect
```

## 📝 Comandos Más Usados

```bash
# Básico - pixel art con 16 colores
python unified_cli.py imagen.jpg --effects pixelart

# Retro completo - múltiples efectos
python unified_cli.py imagen.jpg --effects pixelart chromatic --colors 8 --aberration-intensity 1.5

# Para juegos - sprite 1:1
python pyxelart_refactored.py single imagen.png --aspect-ratio 1:1 --colors 16 --format png

# Procesamiento por lotes
python unified_cli.py --mode batch carpeta/ --output-dir salida/ --effects pixelart --colors 16

# Video retro
python video_processor_refactored.py single video.mp4 --colors 16 --fps 24 --aspect-ratio 4:3
```

## 🎯 Casos de Uso Comunes

### Desarrollo de Videojuegos
```bash
# Convertir arte moderno a pixel art
python pyxelart_refactored.py batch assets/ --output-dir sprites/ --colors 16 --pixel-size 2

# UI retro
python unified_cli.py ui_elements/ --mode batch --effects pixelart --colors 8 --aspect-ratio 1:1
```

### Contenido para Redes Sociales
```bash
# Instagram (1:1)
python unified_cli.py foto.jpg --effects pixelart --aspect-ratio 1:1 --colors 32

# TikTok vertical
python unified_cli.py video.mp4 --effects pixelart --aspect-ratio 9:16 --colors 16
```

### Arte y Diseño
```bash
# Efecto CRT vintage
python unified_cli.py imagen.jpg --effects pixelart chromatic --colors 64 --aberration-intensity 1.0 --aspect-ratio 4:3

# Estilo 8-bit extremo
python unified_cli.py imagen.jpg --effects pixelart --colors 4 --pixel-size 8
```

## 🆘 Solución Rápida de Problemas

### ❌ "Module not found"
```bash
# Asegúrate de estar en el entorno virtual
source .venv/bin/activate
```

### ❌ "FFmpeg not found"
```bash
# Instalar FFmpeg (solo para videos)
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Ubuntu
```

### ❌ Archivo muy grande
```bash
# Reducir calidad
python unified_cli.py imagen_grande.jpg --effects pixelart --format webp --quality 80
```

### ❌ Proceso muy lento
```bash
# Usar menos colores y pixel size mayor
python unified_cli.py imagen.jpg --effects pixelart --colors 8 --pixel-size 6
```

## 📋 Cheat Sheet de Parámetros

```bash
# Efectos
--effects pixelart          # Pixel art
--effects chromatic         # Aberración cromática  
--effects pixelart chromatic dialog  # Múltiples efectos

# Pixel Art
--colors 16                 # Menos colores = más retro (4, 8, 16, 32, 64)
--pixel-size 4              # Mayor = más pixelado (1-20)
--no-noise                  # Sin ruido

# Aspecto
--aspect-ratio 4:3          # Retro clásico
--aspect-ratio 1:1          # Cuadrado (Instagram)
--aspect-ratio 16:9         # Moderno

# Calidad
--format webp               # Mejor compresión
--format png                # Sin pérdida
--quality 95                # Alta calidad (1-100)

# Aberración Cromática
--aberration-intensity 1.5  # Intensidad (0.1-5.0)
--lens-effect               # Distorsión de lente

# Video
--fps 24                    # FPS retro
--video-quality 20          # Calidad (0-51, menor = mejor)
```

## 🎨 Presets Recomendados

### Pixel Art Clásico
```bash
python unified_cli.py imagen.jpg --effects pixelart --colors 16 --pixel-size 4 --aspect-ratio 4:3
```

### Estilo Game Boy
```bash
python unified_cli.py imagen.jpg --effects pixelart --colors 4 --pixel-size 6 --aspect-ratio 1:1 --format png
```

### Monitor CRT Vintage
```bash
python unified_cli.py imagen.jpg --effects pixelart chromatic --colors 64 --pixel-size 2 --aberration-intensity 1.0 --aspect-ratio 4:3
```

### Sprite para Juego
```bash
python pyxelart_refactored.py single imagen.png --colors 16 --pixel-size 1 --aspect-ratio 1:1 --format png --quality 100
```

---

**💡 Tip: Empieza con `unified_cli.py` - es la herramienta más versátil!**