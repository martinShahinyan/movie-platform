"""Static reference data: moods, genres, TMDB genre mapping, baseline mood heuristics."""

MOODS: list[tuple[str, str]] = [
    ("Sad", "sad"),
    ("Happy", "happy"),
    ("Romantic", "romantic"),
    ("Lonely", "lonely"),
    ("Dark", "dark"),
    ("Funny", "funny"),
    ("Cozy", "cozy"),
    ("Atmospheric", "atmospheric"),
    ("Emotional", "emotional"),
    ("Thought-provoking", "thought-provoking"),
    ("Motivational", "motivational"),
    ("Scary", "scary"),
    ("Intense", "intense"),
    ("Chill", "chill"),
    ("Nostalgic", "nostalgic"),
    ("Mind-bending", "mind-bending"),
]

GENRES: list[tuple[str, str]] = [
    ("Drama", "drama"),
    ("Comedy", "comedy"),
    ("Horror", "horror"),
    ("Thriller", "thriller"),
    ("Sci-Fi", "sci-fi"),
    ("Romance", "romance"),
    ("Action", "action"),
    ("Adventure", "adventure"),
    ("Mystery", "mystery"),
    ("Crime", "crime"),
    ("Fantasy", "fantasy"),
    ("Animation", "animation"),
    ("Documentary", "documentary"),
]

# TMDB genre id -> our genre slug (TMDB genres we don't expose are ignored)
TMDB_GENRE_TO_SLUG: dict[int, str] = {
    18: "drama", 35: "comedy", 27: "horror", 53: "thriller", 878: "sci-fi",
    10749: "romance", 28: "action", 12: "adventure", 9648: "mystery",
    80: "crime", 14: "fantasy", 16: "animation", 99: "documentary",
}

# Baseline mood tags assigned ONCE on first import. This is only a starting point;
# moods are curated later through the admin section (Phase 13).
GENRE_TO_MOODS: dict[str, list[str]] = {
    "drama": ["emotional", "sad"],
    "comedy": ["funny", "happy", "chill"],
    "horror": ["scary", "dark", "intense"],
    "thriller": ["intense", "dark"],
    "sci-fi": ["mind-bending", "atmospheric"],
    "romance": ["romantic", "emotional", "cozy"],
    "action": ["intense"],
    "adventure": ["motivational"],
    "mystery": ["atmospheric", "mind-bending"],
    "crime": ["dark"],
    "fantasy": ["cozy", "atmospheric"],
    "animation": ["cozy", "nostalgic"],
    "documentary": ["thought-provoking"],
}
MAX_BASELINE_MOODS = 4
