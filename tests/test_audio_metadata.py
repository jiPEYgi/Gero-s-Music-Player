import unittest
from io import BytesIO
from unittest.mock import patch

from PIL import Image

from audio_metadata import _extract_cover, extract_audio_metadata, resolve_title


def _png_bytes(color=(255, 0, 0, 255)):
    buffer = BytesIO()
    Image.new("RGBA", (2, 2), color).save(buffer, format="PNG")
    return buffer.getvalue()


class _FakeFrame:
    def __init__(self, data, picture_type=None):
        self.data = data
        self.type = picture_type


class _FakeAudio:
    def __init__(self, tags=None, pictures=None, info=None):
        self.tags = tags or {}
        self.pictures = pictures
        self.info = info


class _FakeTags(dict):
    def __init__(self, *args, apic=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.apic = apic or []

    def getall(self, key):
        if key == "APIC":
            return self.apic
        return []


class TestAudioMetadata(unittest.TestCase):
    def test_resolve_title_uses_fallback_filename(self):
        self.assertEqual(resolve_title(None, "music/My Song.mp3"), "My Song")

    def test_resolve_title_reads_values(self):
        self.assertEqual(resolve_title(["  Song Title  "], "music/file.mp3"), "Song Title")

    def test_extract_cover_ignores_invalid_embedded_image(self):
        audio = _FakeAudio(tags={"APIC:Cover": _FakeFrame(b"not-an-image")})
        self.assertIsNone(_extract_cover(audio))

    def test_extract_cover_reads_mp3_apic_frames(self):
        cover = _extract_cover(_FakeAudio(tags=_FakeTags(apic=[_FakeFrame(_png_bytes())])))
        self.assertIsNotNone(cover)
        self.assertEqual(cover.mode, "RGBA")
        self.assertEqual(cover.size, (2, 2))

    def test_extract_cover_reads_flac_or_wav_pictures(self):
        cover = _extract_cover(_FakeAudio(pictures=[_FakeFrame(_png_bytes((0, 255, 0, 128)))]))
        self.assertIsNotNone(cover)
        self.assertEqual(cover.getpixel((0, 0)), (0, 255, 0, 128))

    def test_extract_cover_prefers_front_cover(self):
        cover = _extract_cover(
            _FakeAudio(
                pictures=[
                    _FakeFrame(_png_bytes((255, 0, 0, 255)), picture_type=4),
                    _FakeFrame(_png_bytes((0, 0, 255, 255)), picture_type=3),
                ]
            )
        )
        self.assertEqual(cover.getpixel((0, 0)), (0, 0, 255, 255))

    def test_extract_audio_metadata_handles_reader_error(self):
        with patch("audio_metadata.MutagenFile", side_effect=RuntimeError("broken")):
            metadata = extract_audio_metadata("music/demo.flac")
        self.assertEqual(metadata.title, "demo")
        self.assertIsNone(metadata.cover_image)
        self.assertIsNone(metadata.duration)


if __name__ == "__main__":
    unittest.main()
