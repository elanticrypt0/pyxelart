# PyxelArt Web UI - Quick Start Guide

## 🚀 Inicio Rápido (3 pasos)

### 1. Iniciar el Servidor
```bash
source .venv/bin/activate
python3 app.py
```

Deberías ver:
```
🎨 PyxelArt Web Application
📡 Server: http://localhost:5000
```

### 2. Abrir en Navegador
Ir a: **http://localhost:5000**

### 3. Usar la Aplicación
1. Arrastra una imagen al área de dropzone (o haz clic en "Seleccionar archivo")
2. Ajusta los efectos con los sliders (Pixel Art viene activado por defecto)
3. Espera 500ms para ver el preview actualizado
4. Haz clic en "Exportar Imagen" para descargar

---

## 🎨 Efectos Disponibles

### Pixel Art (activado por defecto)
- **Colores**: 4-256 (menos colores = más retro)
- **Tamaño Pixel**: 1-20 (más grande = más pixelado)
- **Ruido**: 0-50 (agrega textura retro)

### Chromatic Aberration
- **Intensidad**: 0.1-5.0 (separación de canales RGB)
- **Efecto de lente**: Checkbox (distorsión radial)

### Glitch Effects
- **Scanlines**: Líneas horizontales estilo CRT
- **Blocks**: Bloques desplazados aleatoriamente

### Dialog Box
- Agrega cuadro de diálogo retro con texto personalizado

---

## 💾 Presets Predefinidos

Haz clic en cualquiera de estos botones para aplicar configuraciones preestablecidas:

| Preset | Descripción |
|--------|-------------|
| **8-bit** | 8 colores, pixel size 6, ruido alto |
| **16-bit** | 16 colores, pixel size 4, ruido medio |
| **CRT** | Efecto de monitor CRT completo (chromatic + scanlines) |
| **Game Over** | Pantalla de Game Over retro |

**También puedes:**
- Guardar tus propios presets (botón "Guardar Preset")
- Cargar presets desde archivo JSON (botón "Cargar Preset")
- Exportar presets guardados (botón 💾 en la lista)

---

## 📥 Exportación

### Formatos Disponibles
- **PNG**: Sin pérdida, soporta transparencia (sin control de calidad)
- **JPG**: Comprimido, ideal para web (calidad 1-100)
- **WebP**: Comprimido moderno, mejor que JPG (calidad 1-100)
- **TIFF**: Alta calidad, 300 DPI automático

### Cómo Exportar
1. Selecciona el formato en el dropdown
2. Ajusta la calidad (1-100) si aplica
3. Haz clic en "Exportar Imagen"
4. El archivo se descargará automáticamente como `pyxelart_[timestamp].[ext]`

---

## 🔍 Comparación Antes/Después

1. Carga una imagen y aplica efectos
2. Haz clic en el botón **"👁️ Comparar"**
3. Arrastra el slider para revelar la imagen original vs procesada
4. Haz clic de nuevo para volver al modo preview

---

## ⚡ Aplicar en Alta Resolución

Por defecto, el preview se genera en baja resolución (máx 800px) para velocidad.

Para aplicar efectos en **alta resolución completa**:
1. Ajusta todos los efectos como desees
2. Haz clic en **"⚡ Aplicar Full-Res"**
3. Espera a que se procese (puede tomar más tiempo)
4. Exporta la imagen

---

## 🐛 Troubleshooting

### Si algo no funciona:

1. **Abre la consola del navegador** (F12)

2. **Ejecuta el script de debug**:
   ```javascript
   PyxelDebug.runAll()
   ```

3. **Revisa los resultados**:
   - Si todos los checks están ✅, la app debería funcionar
   - Si hay ❌, mira los detalles en la consola

4. **Quick Fixes**:
   ```javascript
   // Recargar la app
   PyxelDebug.fixes.reinit()

   // Limpiar localStorage (si los presets causan problemas)
   PyxelDebug.fixes.clearStorage()

   // Forzar preview
   PyxelDebug.fixes.forcePreview()

   // Cargar imagen de prueba
   PyxelDebug.fixes.testUpload()
   ```

### Problemas Comunes

**Preview no se actualiza**:
- Espera 500ms después de cambiar un slider
- O usa `PyxelDebug.fixes.forcePreview()`

**Botones de preset no funcionan**:
- Verifica en consola: `PyxelDebug.runAll()`
- Prueba: `window.presetUI.applyPredefinedPreset('retro_8bit')`

**Error al exportar**:
- Verifica que hayas cargado una imagen
- Verifica que se haya aplicado al menos un efecto

---

## 📚 Documentación Completa

- **WEB_UI.md**: Guía completa de la interfaz web
- **TROUBLESHOOTING.md**: Guía de troubleshooting detallada
- **API_REST.md**: Documentación de la API backend

---

## ✅ Verificación Rápida

### Backend
```bash
python3 test_web_ui.py
```
Debería mostrar: `4/4 tests passed`

### Frontend
1. Abrir: http://localhost:5000?debug
2. Esperar 2 segundos
3. Ver resultados en consola

---

## 💡 Tips

- **Performance**: Para imágenes grandes (>5MB), usa el preview primero para ajustar, luego aplica full-res
- **Batch**: Carga múltiples archivos arrastrándolos juntos (funcionalidad básica implementada)
- **Keyboard**: Puedes usar Tab para navegar entre controles
- **Mobile**: La interfaz es responsive, pero funciona mejor en desktop

---

## 🎯 Workflow Recomendado

1. **Carga tu imagen**
2. **Prueba un preset predefinido** (8-bit, 16-bit, CRT, Game Over)
3. **Ajusta los parámetros** a tu gusto
4. **Compara antes/después** con el slider
5. **Si te gusta, guarda tu preset** para reutilizarlo
6. **Aplica full-res** si la imagen es grande
7. **Exporta** en el formato que necesites

---

¡Disfruta creando arte retro! 🎨✨
