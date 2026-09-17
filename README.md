# Gero's Music Player

Music player I made out of pure boredom. 

## Instalación

Instala las dependencias:

```bash
pip install customtkinter pygame pillow mutagen
```

## Uso

Coloca tus archivos de audio dentro de la carpeta `music/` en la raíz del proyecto.
El reproductor detecta automáticamente archivos con extensiones `.wav`, `.mp3` y `.flac` (sin importar mayúsculas/minúsculas en la extensión).
Ahora también intenta mostrar el título y la portada embebida de cada canción (si están disponibles).
Incluye controles para reproducir, pausar/reanudar, avanzar/retroceder y una barra de progreso para buscar dentro del tema.