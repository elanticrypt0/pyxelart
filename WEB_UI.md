# PyxelArt Web Interface Documentation

## Introducción

PyxelArt Web Interface es una aplicación web moderna para aplicar efectos retro a imágenes en tiempo real. Cuenta con una interfaz oscura de estilo retro, preview en tiempo real, y sistema completo de presets.

## Inicio Rápido

### 1. Iniciar el Servidor

```bash
# Activar entorno virtual
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Iniciar aplicación
python app.py
```

La aplicación estará disponible en: **http://localhost:5000**

### 2. Usar la Interfaz

1. **Cargar Imagen**: Arrastra una imagen o haz clic en "Seleccionar archivo"
2. **Seleccionar Efectos**: Activa los efectos deseados (Pixel Art, Chromatic, etc.)
3. **Ajustar Parámetros**: Usa los sliders para personalizar cada efecto
4. **Preview en Tiempo Real**: Los cambios se aplican automáticamente
5. **Exportar**: Selecciona formato y calidad, luego descarga

## Características Principales

### 🎨 Efectos Disponibles

#### Pixel Art
- **Colores**: 4-256 colores (default: 16)
- **Tamaño Pixel**: 1-20 (default: 4)
- **Ruido Retro**: Activar/desactivar con intensidad ajustable (0-50)

**Uso**: Ideal para crear sprites estilo 8-bit/16-bit

#### Chromatic Aberration
- **Intensidad**: 0.1-5.0 (default: 1.0)
- **Efecto de Lente**: Activar para aberración radial

**Uso**: Simula distorsión de color estilo CRT o VHS

#### Glitch Effects
- **Scanlines**: Líneas de escaneo CRT (intensidad: 0-1)
- **Glitch Blocks**: Bloques desplazados aleatoriamente (intensidad: 1-50)

**Uso**: Efectos de corrupción digital o estética glitch

#### Dialog Box
- **Texto**: Hasta 20 caracteres
- **Estilo**: Cuadro de diálogo retro estilo RPG

**Uso**: Agregar texto estilo "GAME OVER" o mensajes retro

### 💾 Sistema de Presets

#### Presets Predefinidos

1. **8-bit Retro**
   - 8 colores
   - Pixel size: 6
   - Ruido retro activado

2. **16-bit Retro**
   - 16 colores
   - Pixel size: 4
   - Ruido moderado

3. **CRT Monitor**
   - Pixel art + chromatic + scanlines
   - Simula monitor CRT retro

4. **Game Over**
   - Pixel art + chromatic + dialog "GAME OVER"
   - Pantalla de fin de juego retro

#### Guardar Preset Personalizado

1. Ajusta los efectos y parámetros deseados
2. Haz clic en "Guardar Preset"
3. Introduce un nombre descriptivo
4. El preset se guarda en localStorage y backend

#### Cargar Preset desde Archivo

1. Haz clic en "Cargar Preset"
2. Selecciona un archivo `.json` de preset
3. Los parámetros se aplican automáticamente

#### Exportar Preset

1. Haz clic en el botón 💾 junto al preset guardado
2. Se descarga un archivo `.json` con la configuración

#### Eliminar Preset

1. Haz clic en el botón 🗑️ junto al preset
2. Confirma la eliminación

### 🖼️ Preview y Comparación

#### Preview en Tiempo Real
- Los efectos se aplican automáticamente al modificar parámetros
- Throttling de 500ms para evitar sobrecarga
- Preview en baja resolución (max 800px) para velocidad

#### Comparación Antes/Después
1. Haz clic en "👁️ Comparar"
2. Arrastra el slider para comparar original vs procesado
3. Haz clic nuevamente para volver al preview normal

#### Aplicar Full-Res
- Haz clic en "⚡ Aplicar Full-Res" para procesar en resolución completa
- Útil antes de exportar para máxima calidad

#### Resetear Efectos
- Haz clic en "🔄 Resetear" para volver a configuración por defecto

### 📥 Exportación

#### Formatos Disponibles

1. **PNG** (Lossless)
   - Sin pérdida de calidad
   - Soporta transparencia
   - Tamaño de archivo grande

2. **JPG** (Lossy)
   - Control de calidad: 1-100
   - Sin transparencia
   - Tamaño de archivo pequeño

3. **WebP** (Lossy/Lossless)
   - Control de calidad: 1-100
   - Soporta transparencia
   - Mejor compresión que JPG
   - **Recomendado para web**

4. **TIFF** (Lossless)
   - Formato profesional
   - DPI: 300
   - Compresión LZW
   - Uso profesional/impresión

#### Proceso de Exportación

1. Selecciona **Formato** en el panel de exportación
2. Ajusta **Calidad** (no aplica para PNG)
3. Haz clic en "Exportar Imagen"
4. El archivo se descarga automáticamente con nombre `pyxelart_[timestamp].[formato]`

## Arquitectura Frontend

### Archivos JavaScript

#### `api.js` - Capa de Comunicación
- **API**: Objeto con métodos para todos los endpoints REST
- **ImageUtils**: Utilidades para conversión base64, canvas, descarga

**Métodos principales**:
- `API.generatePreview(imageData, params)`
- `API.applyEffects(imageData, params)`
- `API.exportImage(imageData, format, options)`
- `API.getPresets()` / `savePreset()` / `deletePreset()`

#### `presets.js` - Gestión de Presets
- **PresetManager**: Manejo de presets (crear, cargar, eliminar)
- **PresetUI**: Interfaz de usuario para presets
- **PREDEFINED_PRESETS**: Presets predefinidos (8-bit, 16-bit, CRT, Game Over)

**Características**:
- Almacenamiento en localStorage
- Sincronización con backend
- Exportar/importar JSON
- Renombrar y eliminar presets

#### `effects.js` - Gestión de Efectos
- **EffectsManager**: Controlador principal de efectos y UI
- **ComparisonSlider**: Slider de comparación antes/después

**Características**:
- Preview con throttling (500ms)
- Aplicación de efectos full-res
- Gestión de controles de UI
- Estadísticas en tiempo real

#### `app.js` - Aplicación Principal
- **PyxelArtApp**: Orquestador principal de la aplicación

**Características**:
- Drag & drop de imágenes
- Carga múltiple de archivos
- Procesamiento batch
- Inicialización de componentes

### Flujo de Datos

```
Usuario → Drag&Drop/File Input
    ↓
PyxelArtApp.handleFiles()
    ↓
ImageUtils.fileToBase64()
    ↓
EffectsManager.currentImageData
    ↓
Usuario ajusta parámetros
    ↓
EffectsManager.schedulePreview() [throttled 500ms]
    ↓
API.generatePreview() → Flask Backend
    ↓
Backend procesa (max 800px)
    ↓
EffectsManager.displayPreview()
    ↓
Canvas actualizado
```

### Optimizaciones

#### Preview Rápido
- **Throttling**: 500ms delay entre requests
- **Baja resolución**: Max 800px para preview
- **Cache**: Resultados previos en memoria

#### Full Resolution
- **On-demand**: Solo al hacer clic en "Aplicar Full-Res"
- **Resolución original**: Procesamiento sin reducción
- **Loading indicator**: Feedback visual durante procesamiento

#### Batch Processing
- **Múltiples archivos**: Carga varios archivos a la vez
- **Procesamiento paralelo**: Backend procesa en batch
- **Descarga automática**: Todos los resultados se descargan

## Configuración Avanzada

### Modificar Delay de Preview

En `static/js/effects.js`:
```javascript
this.previewDelay = 500; // ms (cambiar según preferencia)
```

### Modificar Tamaño Máximo de Preview

En `app.py`:
```python
preview_img = MemoryOptimizer.create_preview(img, max_dimension=800)
# Cambiar 800 a valor deseado
```

### Agregar Nuevos Presets Predefinidos

En `static/js/presets.js`:
```javascript
const PREDEFINED_PRESETS = {
    mi_preset: {
        id: 'mi_preset',
        name: 'Mi Preset',
        version: '1.0',
        effects: ['pixelart', 'chromatic'],
        params: {
            colors: 32,
            pixel_size: 3,
            aberration_intensity: 0.8
        }
    }
};
```

Luego agregar botón en `templates/index.html`:
```html
<button class="btn-preset" data-preset="mi_preset">Mi Preset</button>
```

## Solución de Problemas

### Preview no se actualiza
- **Causa**: Error de conexión con backend
- **Solución**: Verificar que Flask esté corriendo en puerto 5000
- **Debug**: Abrir consola del navegador (F12) para ver errores

### Imagen no carga
- **Causa**: Formato no soportado o archivo corrupto
- **Solución**: Usar PNG, JPG, WebP, TIFF válidos
- **Debug**: Verificar en consola mensajes de error

### Efectos muy lentos
- **Causa**: Imagen muy grande o muchos efectos simultáneos
- **Solución**:
  - Reducir resolución de entrada
  - Aplicar menos efectos simultáneamente
  - Aumentar `previewDelay` en effects.js

### Presets no se guardan
- **Causa**: localStorage lleno o backend no disponible
- **Solución**:
  - Limpiar localStorage del navegador
  - Verificar conexión con backend
  - Exportar presets importantes a JSON

### Error 413 (Request Entity Too Large)
- **Causa**: Archivo mayor a 50MB
- **Solución**: Reducir tamaño de imagen antes de cargar
- **Alternativa**: Modificar `MAX_CONTENT_LENGTH` en `app.py`

## Atajos de Teclado (Futuro)

Actualmente la aplicación no tiene atajos de teclado, pero se pueden agregar en `app.js`:

```javascript
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        effectsManager.exportImage();
    }
    if (e.key === 'r') {
        effectsManager.resetEffects();
    }
    if (e.key === 'c') {
        app.toggleComparison();
    }
});
```

## API REST para Integración

Ver `API_REST.md` para documentación completa de endpoints REST.

Endpoints principales:
- `POST /api/preview` - Preview rápido
- `POST /api/apply-effects` - Procesamiento full-res
- `POST /api/export` - Exportar en formato específico
- `GET /api/presets` - Listar presets
- `POST /api/presets` - Guardar preset
- `DELETE /api/presets/:id` - Eliminar preset

## Estructura de Archivos

```
pyxelart/
├── app.py                      # Flask backend
├── templates/
│   └── index.html              # HTML principal
├── static/
│   ├── css/
│   │   └── styles.css          # Estilos CSS
│   ├── js/
│   │   ├── api.js              # Capa de API
│   │   ├── presets.js          # Gestión de presets
│   │   ├── effects.js          # Gestión de efectos
│   │   └── app.js              # Aplicación principal
│   └── images/                 # Assets (opcional)
├── uploads/                    # Archivos temporales
├── outputs/                    # Resultados procesados
└── presets/                    # Presets guardados
```

## Ejemplos de Uso

### Crear un Sprite Retro 8-bit

1. Cargar imagen de personaje
2. Seleccionar preset "8-bit Retro"
3. Ajustar:
   - Colores: 8
   - Pixel Size: 6
   - Ruido: 20
4. Comparar con original usando slider
5. Aplicar Full-Res
6. Exportar como PNG

### Efecto CRT Monitor

1. Cargar screenshot o imagen
2. Seleccionar preset "CRT Monitor"
3. Ajustar scanlines si necesario
4. Exportar como WebP para web

### Pantalla de Game Over

1. Cargar imagen de fondo
2. Seleccionar preset "Game Over"
3. Modificar texto del diálogo
4. Exportar como PNG

## Contribuir

Para agregar nuevos efectos o características:

1. **Backend**: Agregar efecto en `utils/effects_core.py`
2. **API**: Integrar en `app.py` en función `apply_effects_to_image()`
3. **Frontend**:
   - Agregar checkbox en `templates/index.html`
   - Agregar controles específicos del efecto
   - Actualizar `effects.js` para manejar nuevos parámetros
4. **Documentación**: Actualizar este archivo con el nuevo efecto

## Licencia

Ver archivo LICENSE en el repositorio principal.
