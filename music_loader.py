from pathlib import Path


SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac"}


def load_supported_audio_files(directory="music"):
    music_path = Path(directory)
    if not music_path.exists() or not music_path.is_dir():
        print(f"Music directory not found: {music_path}")
        return []

    audio_files = [
        str(path)
        for path in sorted(music_path.iterdir())
        if path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS
    ]

    if not audio_files:
        print(f"No compatible audio files found in {music_path}/")

    return audio_files
