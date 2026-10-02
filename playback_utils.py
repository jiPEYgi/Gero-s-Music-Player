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


DEFAULT_LOCKED_COVER_SIZES = (150, 200, 250, 300, 350, 400, 450, 500)


def calculate_locked_cover_size(
    available_width,
    available_height,
    allowed_sizes=DEFAULT_LOCKED_COVER_SIZES,
):
    if not allowed_sizes:
        return 500
    if available_width is None or available_height is None:
        return allowed_sizes[0]
    available_space = min(available_width, available_height)
    if available_space <= 0:
        return allowed_sizes[0]

    chosen = allowed_sizes[0]
    for size in allowed_sizes:
        if size <= available_space:
            chosen = size
        else:
            break
    return min(chosen, 500)


def format_time(seconds, total_duration=None):
    if seconds is None or seconds < 0:
        seconds = 0.0
    total = total_duration if total_duration is not None and total_duration > 0 else seconds
    sec_int = int(seconds)
    if total >= 3600:
        hours = sec_int // 3600
        minutes = (sec_int % 3600) // 60
        secs = sec_int % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    minutes = sec_int // 60
    secs = sec_int % 60
    return f"{minutes:02d}:{secs:02d}"


def format_volume_percentage(volume_value):
    if volume_value is None:
        return "0%"
    clamped = clamp(float(volume_value))
    return f"{int(round(clamped * 100))}%"


def resolve_next_song_index(current_index, total_songs):
    if total_songs is None or total_songs <= 0:
        return None
    if current_index is None:
        return 0
    next_index = current_index + 1
    if next_index < total_songs:
        return next_index
    return None


