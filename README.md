# Gero's Music Player

Un reproductor de música de escritorio desarrollado con Python, CustomTkinter y Pygame-ce.

## Instalación

Instala las dependencias:

```bash
pip install customtkinter pygame-ce pillow mutagen pyinstaller
```

## Uso

Coloca tus archivos de audio dentro de la carpeta `music/` en la raíz del proyecto (o utiliza el botón **+ Carpeta** para seleccionar cualquier carpeta de tu disco).

### Características:
- **Detección recursiva**: Detecta archivos de audio (`.wav`, `.mp3` y `.flac`) tanto en el directorio raíz seleccionado como en todas sus subcarpetas.
- **Reproducción automática en cadena**: Las canciones se reproducen consecutivamente una tras otra hasta agotar la carpeta, manteniendo una transición limpia entre pistas sin reiniciar estados indebidamente.
- **Soporte para temas largos (>1 hora)**: Lectura optimizada de metadatos y duración sin saturación de memoria, con formato de tiempo extendido (`HH:MM:SS`).
- **Indicador de tiempo transcurrido**: Muestra el tiempo actual transcurrido al lado derecho de la barra de reproducción (actualizándose también al arrastrar para buscar).
- **Indicador de porcentaje de volumen**: Muestra el porcentaje de volumen (`0%` - `100%`) al lado derecho de la barra de volumen.
- **Metadatos y portada**: Muestra artista, título y la portada del álbum embebida si está disponible.

## Compilación / Build del ejecutable

Para generar el ejecutable sin errores de compilación ni dependencias faltantes:

```bash
python build_app.py
```

El resultado final se generará en la carpeta `dist/GerosMusicPlayer/`.
