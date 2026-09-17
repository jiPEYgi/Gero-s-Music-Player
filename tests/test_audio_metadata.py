import unittest
from unittest.mock import patch

from audio_metadata import _extract_cover, extract_audio_metadata, resolve_title


class _FakeFrame:
    def __init__(self, data):
        self.data = data


class _FakeAudio:
    def __init__(self, tags=None, pictures=None, info=None):
        self.tags = tags or {}
        self.pictures = pictures
        self.info = info


class TestAudioMetadata(unittest.TestCase):
    def test_resolve_title_uses_fallback_filename(self):
        self.assertEqual(resolve_title(None, "music/My Song.mp3"), "My Song")

    def test_resolve_title_reads_values(self):
        self.assertEqual(resolve_title(["  Song Title  "], "music/file.mp3"), "Song Title")

    def test_extract_cover_ignores_invalid_embedded_image(self):
        audio = _FakeAudio(tags={"APIC:Cover": _FakeFrame(b"not-an-image")})
        self.assertIsNone(_extract_cover(audio))

    def test_extract_audio_metadata_handles_reader_error(self):
        with patch("audio_metadata.MutagenFile", side_effect=RuntimeError("broken")):
            metadata = extract_audio_metadata("music/demo.flac")
        self.assertEqual(metadata.title, "demo")
        self.assertIsNone(metadata.cover_image)
        self.assertIsNone(metadata.duration)


if __name__ == "__main__":
    unittest.main()
