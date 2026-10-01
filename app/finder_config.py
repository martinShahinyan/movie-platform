"""Options for the "Find my movie" form. One source of truth for HTML and parsing."""

RUNTIME_PRESETS: dict[str, tuple[int | None, int | None]] = {  # value -> (min, max) minutes
    "lt90": (None, 90), "lt120": (None, 120), "lt150": (None, 150), "gt150": (150, None),
}
RUNTIME_OPTIONS = [
    ("", "Any length"), ("lt90", "Under 90 min"), ("lt120", "Under 2 hours"),
    ("lt150", "Under 2.5 hours"), ("gt150", "2.5 hours or more"),
]
RATING_OPTIONS = [("", "Any rating"), ("6", "6+"), ("7", "7+"), ("8", "8+")]
DECADE_OPTIONS = (
    [("", "Any year")]
    + [(str(d), f"{d}s") for d in range(2020, 1960, -10)]
    + [("pre1970", "Before 1970")]
)
LANGUAGE_OPTIONS = [
    ("", "Any language"), ("en", "English"), ("es", "Spanish"), ("fr", "French"), ("de", "German"),
    ("it", "Italian"), ("ja", "Japanese"), ("ko", "Korean"), ("ru", "Russian"),
    ("hi", "Hindi"), ("zh", "Chinese"),
]
FINDER = {
    "runtime": RUNTIME_OPTIONS, "rating": RATING_OPTIONS,
    "decade": DECADE_OPTIONS, "language": LANGUAGE_OPTIONS,
}


def label_for(options: list[tuple[str, str]], value: str) -> str:
    return next((label for v, label in options if v == value), "")
