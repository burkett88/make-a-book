import re


# Rough timing model derived from local test runs (50/100/200/300 words).
# Adjust these as more data is collected.
WORDS_TO_SECONDS = 0.0743
BASE_OVERHEAD_SECONDS = 0.5
SAFETY_FACTOR = 1.3


def count_words(text: str) -> int:
    """Approximate word count for estimation purposes."""
    if not text:
        return 0
    regex_count = len(re.findall(r"\b\w+\b", text))
    split_count = len(text.split())
    return max(regex_count, split_count)


def estimate_tts_seconds(word_count: int, speed: float = 1.0) -> int:
    """Estimate TTS generation time in seconds."""
    if word_count <= 0:
        return 0

    speed = max(speed, 0.25)
    base_seconds = BASE_OVERHEAD_SECONDS + (WORDS_TO_SECONDS * word_count)
    estimated = (base_seconds * SAFETY_FACTOR) / speed
    return max(1, int(round(estimated)))


def format_duration(seconds: int) -> str:
    """Human-readable duration for UI messaging."""
    if seconds <= 0:
        return "0s"

    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"
