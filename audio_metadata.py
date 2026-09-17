from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

try:
    from mutagen import File as MutagenFile
except ImportError:  # pragma: no cover - depends on runtime environment
    MutagenFile = None


@dataclass
class AudioMetadata:
    title: str
    cover_image: Image.Image | None
    duration: float | None


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


def _extract_title(audio):
    tags = getattr(audio, "tags", None)
    if not tags:
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


def _picture_data(picture):
    if isinstance(picture, (bytes, bytearray, memoryview)):
        return bytes(picture)
    return getattr(picture, "data", None)


def _picture_is_front_cover(picture):
    # Mutagen uses type 3 for an explicitly marked front cover.
    return getattr(picture, "type", None) == 3


def _extract_cover(audio):
    """Return the first valid embedded cover, preferring an explicit front cover.

    MP3 files expose APIC frames through ``tags`` while FLAC/WAV files commonly
    expose attached pictures through ``audio.pictures``.  Handling both paths
    keeps the extraction independent of the audio container.
    """
    candidates = []
    tags = getattr(audio, "tags", None)
    if tags:
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
            if str(key).upper().startswith("APIC"):
                if isinstance(value, (list, tuple)):
                    candidates.extend(value)
                else:
                    candidates.append(value)

    candidates.extend(getattr(audio, "pictures", []) or [])

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


def extract_audio_metadata(file_path):
    fallback_title = Path(file_path).stem
    if MutagenFile is None:
        return AudioMetadata(title=fallback_title, cover_image=None, duration=None)

    try:
        audio = MutagenFile(file_path)
    except Exception:
        return AudioMetadata(title=fallback_title, cover_image=None, duration=None)

    if audio is None:
        return AudioMetadata(title=fallback_title, cover_image=None, duration=None)

    title = resolve_title(_extract_title(audio), file_path)
    cover_image = _extract_cover(audio)
    duration = _extract_duration(audio)
    return AudioMetadata(title=title, cover_image=cover_image, duration=duration)
