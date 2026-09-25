import unittest

from playback_utils import (
    calculate_locked_cover_size,
    mixer_elapsed_to_position,
    position_to_progress,
    progress_to_position,
    resolve_playback_action,
    resolve_play_button_text,
)


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

    def test_mixer_elapsed_to_position_handles_invalid_elapsed(self):
        self.assertIsNone(mixer_elapsed_to_position(None, 10))
        self.assertIsNone(mixer_elapsed_to_position(-1, 10))

    def test_mixer_elapsed_to_position_applies_seek_offset(self):
        self.assertEqual(mixer_elapsed_to_position(0, 42.5), 42.5)
        self.assertEqual(mixer_elapsed_to_position(1500, 42.5), 44.0)

    def test_mixer_elapsed_to_position_zero_elapsed_post_seek(self):
        # When seek restarts playback with start=target_seconds, mixer elapsed starts at 0
        target_seek_seconds = 75.0
        self.assertEqual(mixer_elapsed_to_position(0, target_seek_seconds), 75.0)

    def test_seek_and_resume_offset_consistency(self):
        # 1. Song playing initially from start
        playback_offset = 0.0
        elapsed_ms = 10000  # 10 seconds played
        pos = mixer_elapsed_to_position(elapsed_ms, playback_offset)
        self.assertEqual(pos, 10.0)

        # 2. User seeks to 60.0s: playback restarted at 60.0s, elapsed_ms resets to 0
        playback_offset = 60.0
        elapsed_ms = 0
        pos = mixer_elapsed_to_position(elapsed_ms, playback_offset)
        self.assertEqual(pos, 60.0)  # Must be 60.0, no jumping forward

        # 3. Plays for 3 more seconds post-seek
        elapsed_ms = 3000
        pos = mixer_elapsed_to_position(elapsed_ms, playback_offset)
        self.assertEqual(pos, 63.0)

        # 4. User pauses at 63.0s
        paused_pos = pos

        # 5. User resumes: playback_offset is NOT modified because elapsed_ms continues at 3000
        # If playback_offset were wrongly set to paused_pos, pos would wrongly become 63 + 3 = 66
        pos_after_resume = mixer_elapsed_to_position(elapsed_ms, playback_offset)
        self.assertEqual(pos_after_resume, 63.0)
        self.assertEqual(pos_after_resume, paused_pos)


    def test_resolve_playback_action(self):
        self.assertEqual(resolve_playback_action(is_paused=True, is_playing=True), "resume")
        self.assertEqual(resolve_playback_action(is_paused=False, is_playing=True), "pause")
        self.assertEqual(resolve_playback_action(is_paused=False, is_playing=False), "play")

    def test_resolve_play_button_text(self):
        self.assertEqual(resolve_play_button_text(is_paused=True, is_playing=True), "Reanudar")
        self.assertEqual(resolve_play_button_text(is_paused=False, is_playing=True), "Pausar")
        self.assertEqual(resolve_play_button_text(is_paused=False, is_playing=False), "Play")

    def test_calculate_locked_cover_size_handles_none_and_invalid(self):
        self.assertEqual(calculate_locked_cover_size(None, 400), 150)
        self.assertEqual(calculate_locked_cover_size(400, None), 150)
        self.assertEqual(calculate_locked_cover_size(0, 400), 150)
        self.assertEqual(calculate_locked_cover_size(-50, -100), 150)

    def test_calculate_locked_cover_size_locks_to_exact_steps(self):
        self.assertEqual(calculate_locked_cover_size(180, 220), 150)
        self.assertEqual(calculate_locked_cover_size(200, 300), 200)
        self.assertEqual(calculate_locked_cover_size(249, 400), 200)
        self.assertEqual(calculate_locked_cover_size(250, 400), 250)
        self.assertEqual(calculate_locked_cover_size(299, 400), 250)
        self.assertEqual(calculate_locked_cover_size(300, 350), 300)
        self.assertEqual(calculate_locked_cover_size(360, 340), 300)
        self.assertEqual(calculate_locked_cover_size(380, 350), 350)
        self.assertEqual(calculate_locked_cover_size(440, 400), 400)
        self.assertEqual(calculate_locked_cover_size(480, 460), 450)

    def test_calculate_locked_cover_size_caps_at_500(self):
        self.assertEqual(calculate_locked_cover_size(500, 500), 500)
        self.assertEqual(calculate_locked_cover_size(800, 900), 500)
        self.assertEqual(calculate_locked_cover_size(1920, 1080), 500)


if __name__ == "__main__":
    unittest.main()
