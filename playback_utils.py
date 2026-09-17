def clamp(value, minimum=0.0, maximum=1.0):
    return max(minimum, min(maximum, value))


def position_to_progress(position_seconds, duration_seconds):
    if duration_seconds is None or duration_seconds <= 0:
        return 0.0
    if position_seconds is None or position_seconds < 0:
        return 0.0
    return clamp(position_seconds / duration_seconds)


def progress_to_position(progress_value, duration_seconds):
    if duration_seconds is None or duration_seconds <= 0:
        return None
    return clamp(progress_value) * duration_seconds


def mixer_elapsed_to_position(elapsed_ms, start_offset_seconds=0.0):
    if elapsed_ms is None or elapsed_ms < 0:
        return None
    safe_offset = start_offset_seconds if start_offset_seconds and start_offset_seconds > 0 else 0.0
    return safe_offset + (elapsed_ms / 1000.0)


def resolve_playback_action(is_paused, is_playing):
    if is_paused:
        return "resume"
    if is_playing:
        return "pause"
    return "play"


def resolve_play_button_text(is_paused, is_playing):
    if is_paused:
        return "Reanudar"
    if is_playing:
        return "Pausar"
    return "Play"
