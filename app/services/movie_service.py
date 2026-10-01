"""Movie queries and persistence. No HTTP and no HTML in here."""
from __future__ import annotations

import logging
import math
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from typing import Any

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.models import Genre, Movie, Mood, movie_genres, movie_moods
from app.seed_data import GENRE_TO_MOODS, MAX_BASELINE_MOODS, TMDB_GENRE_TO_SLUG

log = logging.getLogger(__name__)

PER_PAGE = 20


@dataclass(frozen=True)
class Page:
    items: list[Movie]
    total: int
    page: int
    per_page: int

    @property
    def pages(self) -> int:
        return max(1, math.ceil(self.total / self.per_page))


def slugify(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")


def build_unique_slug(db: Session, title: str, year: int | None, tmdb_id: int) -> str:
    """title -> title-year -> title-year-tmdbid; non-latin titles fall back to movie-<id>."""
    base = slugify(title) or f"movie-{tmdb_id}"
    candidates = [base]
    if year:
        candidates.append(f"{base}-{year}")
    candidates.append(f"{base}-{tmdb_id}")
    for slug in candidates:
        if not db.scalar(select(Movie.id).where(Movie.slug == slug)):
            return slug
    return candidates[-1]


# ---------- reads ----------

def get_genre(db: Session, slug: str) -> Genre | None:
    return db.scalar(select(Genre).where(Genre.slug == slug))


def get_mood(db: Session, slug: str) -> Mood | None:
    return db.scalar(select(Mood).where(Mood.slug == slug))


def all_moods(db: Session) -> list[Mood]:
    return list(db.scalars(select(Mood).order_by(Mood.id)))


def all_genres(db: Session) -> list[Genre]:
    return list(db.scalars(select(Genre).order_by(Genre.id)))


def moods_with_counts(db: Session) -> list[tuple[Mood, int]]:
    rows = db.execute(
        select(Mood, func.count(movie_moods.c.movie_id))
        .outerjoin(movie_moods, movie_moods.c.mood_id == Mood.id)
        .group_by(Mood.id).order_by(Mood.id)
    ).all()
    return [(m, int(c)) for m, c in rows]


def genres_with_counts(db: Session) -> list[tuple[Genre, int]]:
    rows = db.execute(
        select(Genre, func.count(movie_genres.c.movie_id))
        .outerjoin(movie_genres, movie_genres.c.genre_id == Genre.id)
        .group_by(Genre.id).order_by(Genre.id)
    ).all()
    return [(g, int(c)) for g, c in rows]


def available_years(db: Session) -> list[tuple[int, int]]:
    """(year, movie_count) for every year that has movies, newest first."""
    yr = extract("year", Movie.release_date)
    rows = db.execute(
        select(yr, func.count()).where(Movie.release_date.is_not(None)).group_by(yr).order_by(yr.desc())
    ).all()
    return [(int(y), int(c)) for y, c in rows]


def get_by_slug(db: Session, slug: str) -> Movie | None:
    return db.scalar(select(Movie).where(Movie.slug == slug))


def get_by_tmdb_id(db: Session, tmdb_id: int) -> Movie | None:
    return db.scalar(select(Movie).where(Movie.tmdb_id == tmdb_id))


def list_movies(
    db: Session,
    *,
    page: int = 1,
    per_page: int = PER_PAGE,
    genre_slug: str | None = None,
    mood_slug: str | None = None,
    year: int | None = None,
) -> Page:
    page = max(1, page)
    stmt = select(Movie)
    if genre_slug:
        stmt = stmt.where(Movie.genres.any(Genre.slug == genre_slug))
    if mood_slug:
        stmt = stmt.where(Movie.moods.any(Mood.slug == mood_slug))
    if year:
        stmt = stmt.where(extract("year", Movie.release_date) == year)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(
        stmt.order_by(Movie.vote_count.desc(), Movie.id)
        .limit(per_page)
        .offset((page - 1) * per_page)
    ).all()
    return Page(items=list(items), total=total, page=page, per_page=per_page)


def search_local(db: Session, query: str, limit: int = 10) -> list[Movie]:
    q = query.strip()
    if len(q) < 2:
        return []
    escaped = q.replace("\\", "\\\\").replace("%", r"\%").replace("_", r"\_")
    pattern = f"%{escaped}%"
    stmt = (
        select(Movie)
        .where(Movie.title.ilike(pattern, escape="\\") | Movie.original_title.ilike(pattern, escape="\\"))
        .order_by(Movie.vote_count.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


# ---------- writes ----------

def _parse_date(value: str | None) -> date | None:
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        return None


def upsert_from_tmdb(db: Session, data: dict[str, Any]) -> Movie:
    """Create or update a Movie from a TMDB /movie/{id} payload (idempotent).

    Moods are assigned only on creation, so later manual curation is never overwritten.
    """
    tmdb_id = int(data["id"])
    release = _parse_date(data.get("release_date"))
    movie = get_by_tmdb_id(db, tmdb_id)
    created = movie is None

    if movie is None:
        title = data.get("title") or data.get("original_title") or f"Movie {tmdb_id}"
        movie = Movie(
            tmdb_id=tmdb_id,
            title=title,
            slug=build_unique_slug(db, title, release.year if release else None, tmdb_id),
        )
        db.add(movie)

    movie.title = data.get("title") or movie.title
    movie.original_title = data.get("original_title")
    movie.overview = data.get("overview") or None
    movie.poster_path = data.get("poster_path")
    movie.backdrop_path = data.get("backdrop_path")
    movie.release_date = release
    movie.runtime = data.get("runtime") or None
    movie.vote_average = float(data.get("vote_average") or 0)
    movie.vote_count = int(data.get("vote_count") or 0)
    movie.original_language = data.get("original_language")

    genre_slugs = [
        TMDB_GENRE_TO_SLUG[g["id"]] for g in data.get("genres", []) if g.get("id") in TMDB_GENRE_TO_SLUG
    ]
    genres = list(db.scalars(select(Genre).where(Genre.slug.in_(genre_slugs))).all()) if genre_slugs else []
    movie.genres = genres

    if created:
        movie.moods = _baseline_moods(db, genre_slugs, movie.vote_average)

    db.commit()
    log.info("%s movie %s (tmdb=%s)", "Imported" if created else "Updated", movie.slug, tmdb_id)
    return movie


def _baseline_moods(db: Session, genre_slugs: list[str], vote_average: float) -> list[Mood]:
    wanted: list[str] = []
    for g in genre_slugs:
        for m in GENRE_TO_MOODS.get(g, []):
            if m not in wanted:
                wanted.append(m)
    if vote_average >= 7.8 and "thought-provoking" not in wanted and "drama" in genre_slugs:
        wanted.append("thought-provoking")
    wanted = wanted[:MAX_BASELINE_MOODS]
    if not wanted:
        return []
    return list(db.scalars(select(Mood).where(Mood.slug.in_(wanted))).all())
