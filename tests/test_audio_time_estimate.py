from src.make_a_book.tts_time_estimator import estimate_tts_seconds, format_duration


def _demo_cases() -> list[tuple[int, str]]:
    return [
        (500, "Short story"),
        (1_000, "Picture book"),
        (5_000, "Early reader"),
        (15_000, "Chapter book"),
        (40_000, "Novel"),
    ]


if __name__ == "__main__":
    for words, label in _demo_cases():
        estimate = estimate_tts_seconds(words)
        print(f"{label}: {words} words -> ~{format_duration(estimate)} to generate")
