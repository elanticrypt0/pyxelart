# PyxelArt - Setup para Servidor Casero

## Inicio Rápido con Docker

### 1. Construir y ejecutar
```bash
docker-compose up -d
```

### 2. Acceder a la aplicación
```
http://localhost:5001
```

O desde otro equipo en tu red local:
```
http://[IP-DEL-SERVIDOR]:5001
```

### 3. Ver logs
```bash
docker-compose logs -f
```

### 4. Detener
```bash
docker-compose down
```

## Configuración de Puerto

Edita el archivo `.env`:
```bash
PORT=5001  # Cambia al puerto que prefieras
```

Luego reinicia:
```bash
docker-compose down
docker-compose up -d
```

## Acceso desde otros equipos

Para acceder desde otros dispositivos en tu red:

1. Encuentra la IP de tu servidor:
```bash
ip addr show  # Linux
ipconfig      # Windows
```

2. Asegúrate de que el firewall permite el puerto 5001:
```bash
# Ubuntu/Debian
sudo ufw allow 5001

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5001/tcp
sudo firewall-cmd --reload
```

3. Accede desde otro equipo:
```
http://192.168.1.X:5001
```

## Estructura de Archivos

Los archivos se guardan en:
- `./uploads/` - Imágenes cargadas temporalmente
- `./outputs/` - Imágenes procesadas
- `./presets/` - Presets guardados

Estos directorios persisten entre reinicios del contenedor.

## Comandos Útiles

```bash
# Ver estado
docker-compose ps

# Reiniciar
docker-compose restart

# Rebuild después de actualizaciones
docker-compose up -d --build

# Limpiar todo (CUIDADO: elimina datos)
docker-compose down -v
```

## Troubleshooting

### Puerto en uso
```bash
# Cambia el puerto en .env
PORT=8080

# Reinicia
docker-compose down
docker-compose up -d
```

### No puedo acceder desde otro equipo
1. Verifica que el firewall permite el puerto
2. Verifica que el servidor está en la misma red
3. Prueba con la IP del servidor: `http://[IP]:5001`

### Container no inicia
```bash
# Ver logs detallados
docker-compose logs

# Rebuild desde cero
docker-compose down
docker rmi pyxelart-pyxelart
docker-compose up -d --build
```

## Actualizar la Aplicación

```bash
# Pull últimos cambios
git pull

# Rebuild y reiniciar
docker-compose down
docker-compose up -d --build
```

## Para más información

- `DOCKER.md` - Documentación completa de Docker
- `WEB_UI.md` - Guía de uso de la interfaz web
- `TROUBLESHOOTING.md` - Solución de problemas
- `API_REST.md` - Documentación de la API
