# Gero's Music Player

Un reproductor de música que hice de puro aburrimiento.

## Instalación

Instala las dependencias:

```bash
pip install customtkinter pygame pillow mutagen
```

## Uso

Coloca tus archivos de audio dentro de la carpeta `music/` en la raíz del proyecto.
El reproductor detecta automáticamente archivos con extensiones `.wav`, `.mp3` y `.flac` (sin importar mayúsculas/minúsculas en la extensión).
Ahora también intenta mostrar el título y la portada embebida de cada canción (si están disponibles).
Incluye controles para avanzar/retroceder y una barra de progreso para buscar dentro del tema; el botón **Play** alterna entre reproducir, pausar y reanudar.
