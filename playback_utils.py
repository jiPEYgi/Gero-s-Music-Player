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
