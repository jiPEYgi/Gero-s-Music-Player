import unittest
from unittest.mock import MagicMock, patch

from audio_metadata import AudioMetadata
from playback_utils import calculate_locked_cover_size


class TestUISizing(unittest.TestCase):
    def test_locked_size_breakpoints(self):
        # Steps are (150, 200, 250, 300, 350, 400, 450, 500)
        self.assertEqual(calculate_locked_cover_size(100, 100), 150)
        self.assertEqual(calculate_locked_cover_size(200, 200), 200)
        self.assertEqual(calculate_locked_cover_size(240, 240), 200)
        self.assertEqual(calculate_locked_cover_size(250, 250), 250)
        self.assertEqual(calculate_locked_cover_size(300, 300), 300)
        self.assertEqual(calculate_locked_cover_size(350, 350), 350)
        self.assertEqual(calculate_locked_cover_size(400, 400), 400)
        self.assertEqual(calculate_locked_cover_size(450, 450), 450)
        self.assertEqual(calculate_locked_cover_size(500, 500), 500)
        self.assertEqual(calculate_locked_cover_size(600, 700), 500)
        self.assertEqual(calculate_locked_cover_size(1920, 1080), 500)

    def test_custom_allowed_sizes(self):
        custom = (100, 200, 300)
        self.assertEqual(calculate_locked_cover_size(50, 50, allowed_sizes=custom), 100)
        self.assertEqual(calculate_locked_cover_size(150, 150, allowed_sizes=custom), 100)
        self.assertEqual(calculate_locked_cover_size(200, 200, allowed_sizes=custom), 200)
        self.assertEqual(calculate_locked_cover_size(500, 500, allowed_sizes=custom), 300)


if __name__ == "__main__":
    unittest.main()
