from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError

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
            return image.convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError):
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


def _extract_cover(audio):
    tags = getattr(audio, "tags", None)
    if tags:
        if hasattr(tags, "getall"):
            for frame in tags.getall("APIC"):
                image = _image_from_bytes(getattr(frame, "data", None))
                if image is not None:
                    return image
        for key, value in tags.items():
            if str(key).startswith("APIC"):
                image = _image_from_bytes(getattr(value, "data", None))
                if image is not None:
                    return image

    for picture in getattr(audio, "pictures", []) or []:
        image = _image_from_bytes(getattr(picture, "data", None))
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
