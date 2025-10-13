# PyxelArt - Docker Setup

Guía rápida para ejecutar PyxelArt en Docker.

## Requisitos

- Docker instalado
- Docker Compose instalado

## Inicio Rápido

### 1. Clonar el repositorio
```bash
git clone <tu-repo>
cd pyxelart
```

### 2. Configurar puerto (opcional)
Edita el archivo `.env` para cambiar el puerto:
```bash
PORT=5001  # Cambia esto si necesitas otro puerto
```

### 3. Iniciar la aplicación
```bash
docker-compose up -d
```

La aplicación estará disponible en: `http://localhost:5001`

## Comandos Útiles

### Ver logs
```bash
docker-compose logs -f
```

### Detener la aplicación
```bash
docker-compose down
```

### Reiniciar después de cambios
```bash
docker-compose down
docker-compose up -d --build
```

### Ver estado del contenedor
```bash
docker-compose ps
```

### Entrar al contenedor
```bash
docker-compose exec pyxelart bash
```

## Persistencia de Datos

Los siguientes directorios están montados como volúmenes y persisten entre reinicios:

- `./uploads/` - Archivos cargados temporalmente
- `./outputs/` - Archivos procesados
- `./presets/` - Presets guardados por los usuarios

## Configuración Avanzada

### Cambiar puerto

1. Edita `.env`:
```bash
PORT=8080
```

2. Reinicia:
```bash
docker-compose down
docker-compose up -d
```

### Variables de entorno disponibles

En el archivo `.env` puedes configurar:
- `PORT` - Puerto de la aplicación (default: 5001)

## Troubleshooting

### El puerto ya está en uso
```bash
# Cambia el puerto en .env
PORT=5002

# Reinicia
docker-compose down
docker-compose up -d
```

### Problemas con FFmpeg
FFmpeg está incluido en la imagen Docker, no necesitas instalarlo manualmente.

### Limpiar volúmenes
```bash
# ADVERTENCIA: Esto eliminará todos los datos persistentes
docker-compose down -v
```

### Rebuild completo
```bash
# Eliminar imagen existente y rebuild
docker-compose down
docker rmi pyxelart-pyxelart
docker-compose up -d --build
```

## Arquitectura

La imagen Docker incluye:
- Python 3.11-slim
- FFmpeg (para procesamiento de video)
- Todas las dependencias de Python
- Health check automático
- Restart policy (unless-stopped)

## Producción

Para producción, considera:
- Usar Nginx como reverse proxy
- Configurar HTTPS con Let's Encrypt
- Limitar recursos del contenedor
- Implementar rate limiting
- Configurar logs externos

## Soporte

Para más información:
- Ver `TODO.md` sección "Docker Setup"
- Ver `TROUBLESHOOTING.md` para problemas comunes
- Ver `WEB_UI.md` para uso de la interfaz web
