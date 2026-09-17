import tempfile
import unittest
from pathlib import Path

from music_loader import load_supported_audio_files


class TestMusicLoader(unittest.TestCase):
    def test_detects_supported_files_with_arbitrary_names(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            music_dir = Path(temp_dir)
            (music_dir / "my-song.mp3").write_text("x", encoding="utf-8")
            (music_dir / "RANDOM_TRACK.FLAC").write_text("x", encoding="utf-8")
            (music_dir / "voice.WaV").write_text("x", encoding="utf-8")
            (music_dir / "readme.txt").write_text("x", encoding="utf-8")

            files = load_supported_audio_files(music_dir)

            self.assertEqual(
                files,
                [
                    str(music_dir / "RANDOM_TRACK.FLAC"),
                    str(music_dir / "my-song.mp3"),
                    str(music_dir / "voice.WaV"),
                ],
            )

    def test_returns_empty_when_directory_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_dir = Path(temp_dir) / "music"
            self.assertEqual(load_supported_audio_files(missing_dir), [])

    def test_returns_empty_when_directory_has_no_supported_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            music_dir = Path(temp_dir)
            (music_dir / "notes.txt").write_text("x", encoding="utf-8")
            (music_dir / "cover.jpg").write_text("x", encoding="utf-8")

            self.assertEqual(load_supported_audio_files(music_dir), [])


if __name__ == "__main__":
    unittest.main()
