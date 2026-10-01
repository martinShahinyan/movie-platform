from __future__ import annotations

from pydantic import BaseModel

from app.models import Movie
from app.services.tmdb_service import image_url


class MovieCardOut(BaseModel):
    id: int
    slug: str
    title: str
    year: int | None
    poster_url: str | None
    rating: float
    runtime: int | None
    genres: list[str]
    moods: list[str]

    @classmethod
    def from_movie(cls, m: Movie) -> MovieCardOut:
        return cls(
            id=m.id, slug=m.slug, title=m.title, year=m.year,
            poster_url=image_url(m.poster_path, "w342"), rating=round(m.vote_average, 1),
            runtime=m.runtime, genres=[g.name for g in m.genres], moods=[x.name for x in m.moods],
        )


class MovieDetailOut(MovieCardOut):
    original_title: str | None
    overview: str | None
    backdrop_url: str | None
    vote_count: int
    original_language: str | None

    @classmethod
    def from_movie(cls, m: Movie) -> MovieDetailOut:
        return cls(
            **MovieCardOut.from_movie(m).model_dump(),
            original_title=m.original_title, overview=m.overview,
            backdrop_url=image_url(m.backdrop_path, "w1280"),
            vote_count=m.vote_count, original_language=m.original_language,
        )


class MoviePageOut(BaseModel):
    items: list[MovieCardOut]
    total: int
    page: int
    pages: int


class SearchHitOut(BaseModel):
    slug: str
    title: str
    year: int | None
    poster_url: str | None


class ScoredMovieOut(MovieCardOut):
    score: int


class RecommendationPageOut(BaseModel):
    items: list[ScoredMovieOut]
    total: int
    page: int
    pages: int
    relaxed: bool


class TaxonomyOut(BaseModel):
    name: str
    slug: str
    movie_count: int
