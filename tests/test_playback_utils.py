import unittest

from playback_utils import position_to_progress, progress_to_position


class TestPlaybackUtils(unittest.TestCase):
    def test_position_to_progress_handles_invalid_duration(self):
        self.assertEqual(position_to_progress(10, None), 0.0)
        self.assertEqual(position_to_progress(10, 0), 0.0)

    def test_position_to_progress_clamps_values(self):
        self.assertEqual(position_to_progress(-1, 100), 0.0)
        self.assertEqual(position_to_progress(50, 100), 0.5)
        self.assertEqual(position_to_progress(150, 100), 1.0)

    def test_progress_to_position_handles_invalid_duration(self):
        self.assertIsNone(progress_to_position(0.5, None))
        self.assertIsNone(progress_to_position(0.5, 0))

    def test_progress_to_position_clamps_values(self):
        self.assertEqual(progress_to_position(-0.5, 200), 0.0)
        self.assertEqual(progress_to_position(0.25, 200), 50.0)
        self.assertEqual(progress_to_position(1.5, 200), 200.0)


if __name__ == "__main__":
    unittest.main()
