from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

try:
    from mutagen import File as MutagenFile
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC, Picture as FLACPicture
    from mutagen.id3 import ID3, APIC
    from mutagen.wave import WAVE
except ImportError:  # pragma: no cover - depends on runtime environment
    MutagenFile = None
    MP3 = None
    FLAC = None
    FLACPicture = None
    ID3 = None
    APIC = None
    WAVE = None


@dataclass
class AudioMetadata:
    title: str
    artist: str = "Artista desconocido"
    cover_image: Image.Image | None = None
    duration: float | None = None


def _normalize_text(value):
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else None
    if isinstance(value, (list, tuple)):
        for entry in value:
            normalized = _normalize_text(entry)
            if normalized:
                return normalized
        return None
    if hasattr(value, "text"):
        return _normalize_text(value.text)
    cleaned = str(value).strip()
    return cleaned if cleaned else None


def _image_from_bytes(image_bytes):
    if not image_bytes:
        return None
    try:
        with Image.open(BytesIO(image_bytes)) as image:
            # Copy the decoded image before the BytesIO/Image context is closed.
            # exif_transpose also fixes covers stored with an EXIF orientation tag.
            return ImageOps.exif_transpose(image).convert("RGBA").copy()
    except (UnidentifiedImageError, OSError, ValueError, TypeError):
        return None


def resolve_title(raw_title, file_path):
    return _normalize_text(raw_title) or Path(file_path).stem


def resolve_artist(raw_artist, fallback="Artista desconocido"):
    return _normalize_text(raw_artist) or fallback


def _extract_title(audio):
    tags = getattr(audio, "tags", None)
    if tags is None:
        return None

    for key in ("title", "TIT2"):
        if key in tags:
            title = _normalize_text(tags.get(key))
            if title:
                return title

    for key, value in tags.items():
        if "title" in str(key).lower():
            title = _normalize_text(value)
            if title:
                return title
    return None


def _extract_artist(audio):
    tags = getattr(audio, "tags", None)
    if tags is None:
        return None

    for key in ("artist", "TPE1", "\xa9ART", "TPE2", "albumartist", "aART"):
        if key in tags:
            artist = _normalize_text(tags.get(key))
            if artist:
                return artist

    try:
        tag_items = tags.items()
    except (AttributeError, TypeError):
        tag_items = ()

    for key, value in tag_items:
        key_str = str(key).lower()
        if "artist" in key_str or "author" in key_str:
            artist = _normalize_text(value)
            if artist:
                return artist

    return None


def _picture_data(picture):
    if isinstance(picture, (bytes, bytearray, memoryview)):
        return bytes(picture)
    return getattr(picture, "data", None)


def _picture_is_front_cover(picture):
    # Mutagen uses type 3 for an explicitly marked front cover.
    return getattr(picture, "type", None) == 3


def _find_folder_cover(file_path):
    """Search for album artwork in the same folder as the audio file."""
    try:
        song_path = Path(file_path)
        folder = song_path.parent
        if not folder.is_dir():
            return None

        image_extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
        preferred_names = (
            "cover",
            "folder",
            "front",
            "album",
            "albumart",
            "artwork",
            song_path.stem.lower(),
        )

        for name in preferred_names:
            for ext in image_extensions:
                candidate = folder / f"{name}{ext}"
                if candidate.is_file():
                    try:
                        with open(candidate, "rb") as f:
                            img = _image_from_bytes(f.read())
                            if img is not None:
                                return img
                    except Exception:
                        pass

        for file in sorted(folder.iterdir()):
            if file.is_file() and file.suffix.lower() in image_extensions:
                lower_name = file.stem.lower()
                if any(k in lower_name for k in ("cover", "front", "folder", "album", "art")):
                    try:
                        with open(file, "rb") as f:
                            img = _image_from_bytes(f.read())
                            if img is not None:
                                return img
                    except Exception:
                        pass
    except Exception:
        pass
    return None


def _extract_cover(audio):
    """Return the first valid embedded cover, preferring an explicit front cover.

    MP3 files expose APIC frames through ``tags`` while FLAC/WAV files commonly
    expose attached pictures through ``audio.pictures``.  Handling both paths
    keeps the extraction independent of the audio container.
    """
    candidates = []
    tags = getattr(audio, "tags", None)
    if tags is not None:
        if hasattr(tags, "getall"):
            try:
                candidates.extend(tags.getall("APIC"))
            except (KeyError, TypeError, AttributeError):
                pass

        try:
            tag_items = tags.items()
        except (AttributeError, TypeError):
            tag_items = ()
        for key, value in tag_items:
            key_str = str(key).upper()
            if key_str.startswith("APIC") or key_str in ("COVR", "METADATA_BLOCK_PICTURE"):
                if isinstance(value, (list, tuple)):
                    candidates.extend(value)
                else:
                    candidates.append(value)

        # Also inspect tag values for ID3 APIC frames
        try:
            tag_vals = tags.values()
        except (AttributeError, TypeError):
            tag_vals = ()
        for val in tag_vals:
            if hasattr(val, "data") and getattr(val, "FrameID", None) == "APIC" and val not in candidates:
                candidates.append(val)

    candidates.extend(getattr(audio, "pictures", []) or [])

    # Handle base64-encoded metadata_block_picture in OGG/FLAC if present as string/bytes
    for item in list(candidates):
        if isinstance(item, (str, bytes)) and not hasattr(item, "data"):
            try:
                import base64
                raw_bytes = base64.b64decode(item)
                if FLACPicture is not None:
                    candidates.append(FLACPicture(raw_bytes))
                else:
                    candidates.append(raw_bytes)
            except Exception:
                pass

    # Stable ordering: explicit front covers first, then all other pictures.
    candidates.sort(key=lambda picture: not _picture_is_front_cover(picture))
    for picture in candidates:
        image = _image_from_bytes(_picture_data(picture))
        if image is not None:
            return image
    return None


def _extract_duration(audio):
    info = getattr(audio, "info", None)
    length = getattr(info, "length", None)
    if length and length > 0:
        return float(length)
    return None


def _extract_duration_fallback(file_path):
    path = Path(file_path)
    if not path.is_file():
        return None
    ext = path.suffix.lower()

    if ext == ".wav":
        try:
            import wave
            with wave.open(str(file_path), "rb") as wf:
                framerate = wf.getframerate()
                nframes = wf.getnframes()
                if framerate > 0 and nframes > 0:
                    return float(nframes) / float(framerate)
        except Exception:
            pass

    if ext == ".mp3" and MP3 is not None:
        try:
            audio = MP3(str(file_path))
            info = getattr(audio, "info", None)
            length = getattr(info, "length", None)
            if length and length > 0:
                return float(length)
        except Exception:
            pass

    if ext == ".flac" and FLAC is not None:
        try:
            audio = FLAC(str(file_path))
            info = getattr(audio, "info", None)
            length = getattr(info, "length", None)
            if length and length > 0:
                return float(length)
        except Exception:
            pass

    try:
        import pygame
        if pygame.mixer.get_init():
            snd = pygame.mixer.Sound(str(file_path))
            length = snd.get_length()
            if length and length > 0:
                return float(length)
    except Exception:
        pass

    return None


def extract_audio_metadata(file_path):
    fallback_title = Path(file_path).stem
    fallback_artist = "Artista desconocido"

    audio = None
    if MutagenFile is not None:
        try:
            audio = MutagenFile(file_path)
        except Exception:
            audio = None

    if audio is None and MutagenFile is not None:
        ext = Path(file_path).suffix.lower()
        try:
            if ext == ".mp3" and MP3 is not None:
                audio = MP3(str(file_path))
            elif ext == ".flac" and FLAC is not None:
                audio = FLAC(str(file_path))
            elif ext == ".wav" and WAVE is not None:
                audio = WAVE(str(file_path))
        except Exception:
            audio = None

    title = resolve_title(_extract_title(audio), file_path) if audio is not None else fallback_title
    artist = resolve_artist(_extract_artist(audio), fallback=fallback_artist) if audio is not None else fallback_artist

    cover_image = _extract_cover(audio) if audio is not None else None
    if cover_image is None:
        cover_image = _find_folder_cover(file_path)

    duration = _extract_duration(audio) if audio is not None else None
    if duration is None:
        duration = _extract_duration_fallback(file_path)

    return AudioMetadata(title=title, artist=artist, cover_image=cover_image, duration=duration)

