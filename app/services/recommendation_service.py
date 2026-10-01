"""Deterministic recommendation engine. No HTTP, no HTML, no AI.

An AI layer can later translate free text into a `RecommendationQuery` (see `from_filters`);
the engine itself never invents movies - everything comes from our own database.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import Any

from sqlalchemy import and_, case, func, literal, or_, select
from sqlalchemy.orm import Session

from app.models import Genre, Movie, Mood, movie_genres, movie_moods

WEIGHTS = {"mood": 5, "genre": 3, "runtime": 2, "rating": 2, "year": 1, "language": 1}
RELAX_BELOW = 6  # fewer strict matches than this -> fall back to "closest matches"
PER_PAGE = 20


@dataclass(frozen=True)
class RecommendationQuery:
    moods: tuple[str, ...] = ()
    genres: tuple[str, ...] = ()
    min_runtime: int | None = None
    max_runtime: int | None = None
    min_rating: float | None = None
    year_from: int | None = None
    year_to: int | None = None
    language: str | None = None

    @property
    def has_targets(self) -> bool:
        return bool(self.moods or self.genres)

    @property
    def has_constraints(self) -> bool:
        return any(v is not None for v in (
            self.min_runtime, self.max_runtime, self.min_rating,
            self.year_from, self.year_to, self.language))

    @classmethod
    def from_filters(cls, data: dict[str, Any]) -> RecommendationQuery:
        """Build a query from structured filters, e.g. the future AI output:
        {"moods": ["lonely", "emotional"], "genres": ["drama"], "intensity": "medium", "runtime": null}
        Unknown keys (like "intensity") are ignored for now."""
        runtime = data.get("runtime")
        return cls(
            moods=tuple(data.get("moods") or ()), genres=tuple(data.get("genres") or ()),
            max_runtime=runtime if isinstance(runtime, int) else data.get("max_runtime"),
            min_runtime=data.get("min_runtime"), min_rating=data.get("min_rating"),
            year_from=data.get("year_from"), year_to=data.get("year_to"),
            language=data.get("language"),
        )


@dataclass(frozen=True)
class Recommendation:
    movie: Movie
    score: int


@dataclass(frozen=True)
class RecommendationPage:
    items: list[Recommendation]
    total: int
    page: int
    per_page: int
    relaxed: bool = False

    @property
    def pages(self) -> int:
        return max(1, math.ceil(self.total / self.per_page))


def _hits(link, fk, model, slugs: tuple[str, ...]):
    """Number of the movie's moods/genres that are in `slugs` (correlated scalar subquery)."""
    if not slugs:
        return literal(0)
    return (
        select(func.count()).select_from(link)
        .where(link.c.movie_id == Movie.id, fk.in_(select(model.id).where(model.slug.in_(slugs))))
        .scalar_subquery()
    )


def _constraint_predicates(q: RecommendationQuery) -> dict[str, Any]:
    preds: dict[str, Any] = {}
    if q.min_runtime is not None or q.max_runtime is not None:
        parts = [Movie.runtime.is_not(None)]
        if q.min_runtime is not None:
            parts.append(Movie.runtime >= q.min_runtime)
        if q.max_runtime is not None:
            parts.append(Movie.runtime <= q.max_runtime)
        preds["runtime"] = and_(*parts)
    if q.min_rating is not None:
        preds["rating"] = Movie.vote_average >= q.min_rating
    if q.year_from is not None or q.year_to is not None:
        parts = [Movie.release_date.is_not(None)]
        if q.year_from is not None:
            parts.append(Movie.release_date >= date(q.year_from, 1, 1))
        if q.year_to is not None:
            parts.append(Movie.release_date <= date(q.year_to, 12, 31))
        preds["year"] = and_(*parts)
    if q.language:
        preds["language"] = Movie.original_language == q.language
    return preds


def recommend(
    db: Session,
    q: RecommendationQuery,
    *,
    page: int = 1,
    per_page: int = PER_PAGE,
    allow_relax: bool = True,
) -> RecommendationPage:
    """Score = 5/mood match + 3/genre match + 2 runtime + 2 rating + 1 year + 1 language.

    Strict mode: runtime, rating, year and language act as hard filters, and a movie must
    match at least one selected mood/genre. If that leaves fewer than RELAX_BELOW movies and
    `allow_relax` is set, the constraints become score-only ("closest matches").
    Scoring runs in SQL, so pagination never loads the whole catalogue.
    """
    page = max(1, page)
    mood_hits = _hits(movie_moods, movie_moods.c.mood_id, Mood, q.moods)
    genre_hits = _hits(movie_genres, movie_genres.c.genre_id, Genre, q.genres)
    preds = _constraint_predicates(q)

    score = mood_hits * WEIGHTS["mood"] + genre_hits * WEIGHTS["genre"]
    for name, pred in preds.items():
        score = score + case((pred, WEIGHTS[name]), else_=0)

    gate = [or_(mood_hits > 0, genre_hits > 0)] if q.has_targets else []
    strict_where = gate + list(preds.values())

    total = db.scalar(select(func.count()).select_from(Movie).where(*strict_where)) or 0
    where, relaxed = strict_where, False
    if allow_relax and preds and total < RELAX_BELOW:
        where, relaxed = gate, True
        total = db.scalar(select(func.count()).select_from(Movie).where(*where)) or 0

    # Tie-break: rating, discounted when few people have voted (avoids a 10.0 from 3 votes).
    quality = case(
        (Movie.vote_count >= 500, Movie.vote_average),
        else_=Movie.vote_average * Movie.vote_count / 500.0,
    )
    rows = db.execute(
        select(Movie, score.label("score")).where(*where)
        .order_by(score.desc(), quality.desc(), Movie.id)
        .limit(per_page).offset((page - 1) * per_page)
    ).all()
    return RecommendationPage(
        items=[Recommendation(movie=m, score=int(s)) for m, s in rows],
        total=total, page=page, per_page=per_page, relaxed=relaxed,
    )
