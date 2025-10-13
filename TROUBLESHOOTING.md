# PyxelArt Web UI - Troubleshooting Guide

## Estado Actual (2025-10-05)

### ✅ Componentes Funcionando
- **Backend API REST**: 100% funcional
  - `/health` - Health check ✅
  - `/api/effects` - Listar efectos ✅
  - `/api/preview` - Generar preview ✅
  - `/api/apply-effects` - Aplicar efectos full-res ✅
  - `/api/presets` - CRUD de presets ✅
  - `/api/export` - Exportar en múltiples formatos ✅
  - `/api/batch-process` - Procesamiento batch ✅

- **Archivos Frontend**: Completos
  - `templates/index.html` - ✅
  - `static/css/styles.css` - ✅
  - `static/js/api.js` - ✅
  - `static/js/effects.js` - ✅
  - `static/js/presets.js` - ✅
  - `static/js/app.js` - ✅

### 🔍 Problemas Potenciales Identificados

#### 1. **Funcionalidad que puede no estar funcionando**
Basado en el análisis del código, estos son los posibles problemas:

##### a) Botones de Presets Predefinidos
**Síntoma**: Los botones de presets predefinidos (8-bit, 16-bit, CRT, Game Over) no aplican efectos.

**Causa**: Event listeners se configuran en `PresetUI.init()` pero pueden ejecutarse antes de que el DOM esté listo.

**Solución**: Los event listeners están correctamente configurados en `presets.js:333-338`. Si no funcionan:
1. Abrir consola del navegador (F12)
2. Verificar errores de JavaScript
3. Verificar que `window.effectsManager` esté definido

**Test manual**:
```javascript
// En consola del navegador:
console.log(window.presetUI);
console.log(window.effectsManager);
```

##### b) Preview en Tiempo Real
**Síntoma**: El preview no se actualiza al cambiar sliders.

**Causa posible**: Throttling de 500ms puede parecer lento en algunas configuraciones.

**Solución**:
- El throttling está configurado en `effects.js:11` como `previewDelay = 500`
- Para pruebas, puedes reducir a 200ms editando la línea 11

##### c) Comparación Antes/Después
**Síntoma**: El botón "Comparar" no muestra el slider.

**Causa**: El slider requiere que existan tanto `currentImageData` como `processedImageData`.

**Solución verificada**:
- El código en `app.js:265-285` maneja correctamente el toggle
- El slider se crea en `effects.js:455-554`

##### d) Exportación de Imágenes
**Síntoma**: El botón "Exportar Imagen" no descarga nada.

**Causa posible**: El endpoint `/api/export` retorna un blob que debe ser manejado correctamente.

**Verificado**: El código en `api.js:104-129` maneja correctamente el blob y en `effects.js:424-449` usa `ImageUtils.downloadBlob()`.

#### 2. **Errores de CORS (si accedes desde otro dominio)**
**Síntoma**: Errores en consola "CORS policy blocked".

**Solución**: El servidor Flask está configurado para aceptar todas las conexiones (`0.0.0.0`), pero puede necesitar headers CORS.

**Fix rápido**: Agregar a `app.py`:
```python
from flask_cors import CORS
CORS(app)
```

#### 3. **Imágenes muy grandes causan timeout**
**Síntoma**: La aplicación se congela al cargar imágenes grandes.

**Solución implementada**:
- El preview usa `MemoryOptimizer` que reduce a máx 800px
- Para imágenes > 10MB, considera usar el botón "Aplicar Full-Res" solo cuando sea necesario

---

## Cómo Probar la Aplicación

### 1. Iniciar el Servidor
```bash
source .venv/bin/activate
python3 app.py
```

Deberías ver:
```
🎨 PyxelArt Web Application
📡 Server: http://localhost:5000
🌐 Web UI: http://localhost:5000
```

### 2. Abrir en Navegador
Ir a: http://localhost:5000

### 3. Test Básico
1. **Cargar una imagen**:
   - Arrastra una imagen JPG/PNG al área de dropzone
   - O haz clic en "Seleccionar archivo"

2. **Verificar que se muestra**:
   - La imagen debe aparecer en el canvas central
   - Info debe mostrarse en panel superior izquierdo (nombre, dimensiones, tamaño)

3. **Aplicar efecto Pixel Art** (ya viene activado por defecto):
   - Mover slider de "Colores" (4-256)
   - Mover slider de "Tamaño Pixel" (1-20)
   - El preview debería actualizarse automáticamente después de 500ms

4. **Probar preset predefinido**:
   - Clic en botón "8-bit"
   - Debería aplicar: 8 colores, pixel size 6, ruido 20

5. **Comparar antes/después**:
   - Clic en botón "👁️ Comparar"
   - Debería mostrar slider para comparar original vs procesado

6. **Exportar**:
   - Seleccionar formato (PNG, JPG, WebP, TIFF)
   - Ajustar calidad (1-100)
   - Clic en "Exportar Imagen"
   - Debería descargar archivo `pyxelart_[timestamp].[ext]`

### 4. Test de Backend (sin UI)
```bash
python3 test_web_ui.py
```

Debería mostrar 4/4 tests pasados.

---

## 🐛 Script de Debug Automático

**NUEVO**: Ahora puedes usar el script de debug integrado para diagnosticar problemas automáticamente.

### Uso del Script de Debug

1. **Abrir la aplicación en el navegador**: http://localhost:5000

2. **Abrir consola del navegador**: Press F12 (o Cmd+Option+I en Mac)

3. **Ejecutar el debug completo**:
   ```javascript
   PyxelDebug.runAll()
   ```

   Esto verificará:
   - ✅ Instancias globales (app, effectsManager, etc.)
   - ✅ Elementos del DOM
   - ✅ Botones de presets
   - ✅ Settings actuales
   - ✅ Imagen cargada
   - ✅ localStorage
   - ✅ Conectividad API
   - ✅ Aplicación de presets

4. **Modo debug automático**: Abre la app con `?debug` en la URL:
   ```
   http://localhost:5000?debug
   ```
   El script de debug se ejecutará automáticamente después de 2 segundos.

### Quick Fixes Disponibles

Desde la consola del navegador:

```javascript
// Recargar la aplicación
PyxelDebug.fixes.reinit()

// Limpiar localStorage (si los presets causan problemas)
PyxelDebug.fixes.clearStorage()

// Forzar actualización de preview
PyxelDebug.fixes.forcePreview()

// Cargar imagen de prueba automáticamente
PyxelDebug.fixes.testUpload()
```

---

## Verificación de Problemas Comunes

### Problema: "No se carga la interfaz web"
**Verificar**:
```bash
# ¿Está corriendo Flask?
curl http://localhost:5000/health

# ¿Existen los archivos estáticos?
ls -la static/css/
ls -la static/js/
ls -la templates/
```

### Problema: "Los efectos no se aplican"
**Debug en consola del navegador**:
```javascript
// Verificar que los managers existan
console.log(window.app);
console.log(window.effectsManager);
console.log(window.presetManager);
console.log(window.presetUI);

// Verificar settings actuales
console.log(window.effectsManager.getCurrentSettings());

// Probar preview manual
window.effectsManager.generatePreview();
```

### Problema: "Los presets predefinidos no funcionan"
**Test manual**:
```javascript
// En consola del navegador
window.presetUI.applyPredefinedPreset('retro_8bit');
```

Si esto funciona pero el botón no, el problema es el event listener.

### Problema: "Error al exportar"
**Verificar**:
```javascript
// En consola del navegador
console.log(window.effectsManager.processedImageData);
```

Si es `null`, primero debes aplicar efectos.

---

## Soluciones Rápidas

### Fix 1: Reiniciar Event Listeners
Si los botones no responden, ejecuta en consola:
```javascript
window.app = new PyxelArtApp();
```

### Fix 2: Limpiar localStorage
Si los presets guardados causan problemas:
```javascript
localStorage.removeItem('pyxelart_presets');
location.reload();
```

### Fix 3: Forzar Preview
Si el preview no se genera:
```javascript
window.effectsManager.previewDelay = 0;
window.effectsManager.schedulePreview();
```

---

## Testing Sistemático

### Test 1: Carga de Imagen
```
[ ] Dropzone acepta archivos
[ ] File input funciona
[ ] Imagen se muestra en canvas
[ ] Info se actualiza (nombre, dimensiones, tamaño)
```

### Test 2: Efectos
```
[ ] Pixel Art checkbox activo por defecto
[ ] Sliders responden
[ ] Preview se actualiza (esperar 500ms)
[ ] Chromatic aberration funciona
[ ] Dialog box funciona
[ ] Glitch effects funcionan
```

### Test 3: Presets
```
[ ] Botón "8-bit" aplica preset
[ ] Botón "16-bit" aplica preset
[ ] Botón "CRT" aplica preset
[ ] Botón "Game Over" aplica preset
[ ] Guardar preset funciona
[ ] Cargar preset desde archivo funciona
[ ] Eliminar preset funciona
```

### Test 4: Exportación
```
[ ] Selector de formato funciona
[ ] Slider de calidad funciona (hidden para PNG)
[ ] Exportar PNG funciona
[ ] Exportar JPG funciona
[ ] Exportar WebP funciona
[ ] Exportar TIFF funciona
```

### Test 5: Comparación
```
[ ] Botón "Comparar" muestra slider
[ ] Slider es draggable
[ ] Revelar funciona correctamente
[ ] Toggle back to preview funciona
```

### Test 6: Batch Processing
```
[ ] Cargar múltiples archivos
[ ] Indicador de batch mode
[ ] Procesar batch (requiere implementación adicional)
```

---

## Estado de Implementación

### ✅ Completado
- Backend API REST completo
- Frontend UI completo
- Sistema de presets
- Preview en tiempo real
- Exportación multi-formato
- Comparación antes/después
- Tests de backend

### ⚠️ Necesita Testing Manual
- Event listeners de presets predefinidos
- Drag & drop de múltiples archivos
- Batch processing via UI
- Cross-browser compatibility

### 📋 No Implementado (Fase 4)
- [ ] WebSocket para procesamiento en tiempo real
- [ ] Caché de previews en IndexedDB
- [ ] Service Worker para offline mode
- [ ] Tests E2E con Playwright
- [ ] Docker deployment
- [ ] Documentación Swagger/OpenAPI

---

## Próximos Pasos Recomendados

1. **Testing manual completo**:
   - Probar cada funcionalidad en navegador
   - Documentar errores específicos encontrados

2. **Agregar logs de debug**:
   - Agregar `console.log()` en event listeners críticos
   - Verificar flujo de datos

3. **Mejorar UX**:
   - Agregar tooltips
   - Agregar keyboard shortcuts
   - Agregar progress bars para batch

4. **Optimización**:
   - Implementar caché de previews
   - Reducir throttling para imágenes pequeñas
   - Lazy loading de efectos

---

## Contacto y Reporte de Bugs

Si encuentras un bug específico:
1. Anotar pasos para reproducir
2. Capturar screenshot
3. Copiar errores de consola (F12)
4. Verificar con `python3 test_web_ui.py` si es backend
5. Verificar en consola del navegador si es frontend

**Comandos útiles para debug**:
```bash
# Ver logs de Flask
source .venv/bin/activate && python3 app.py

# Test backend
python3 test_web_ui.py

# Ver archivos estáticos
tree static/

# Ver presets guardados
cat presets/*.json
```
