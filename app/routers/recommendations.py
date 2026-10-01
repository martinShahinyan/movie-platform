import re
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.finder_config import RUNTIME_PRESETS
from app.schemas.movie import MovieCardOut, RecommendationPageOut, ScoredMovieOut
from app.services import recommendation_service as engine
from app.services.recommendation_service import RecommendationQuery

router = APIRouter(prefix="/api", tags=["recommendations"])

_SLUG = re.compile(r"^[a-z0-9-]{1,60}$")
_LANG = re.compile(r"^[a-z]{2,3}$")
MAX_MOODS = MAX_GENRES = 3


def _slugs(values: list[str], cap: int) -> tuple[str, ...]:
    out: list[str] = []
    for v in values:
        v = v.strip().lower()
        if _SLUG.match(v) and v not in out:
            out.append(v)
    return tuple(out[:cap])


def _num(value: str | None, cast, lo: float, hi: float):
    """Tolerant parsing: blank or invalid values (a GET form sends blanks) mean 'not set'."""
    try:
        n = cast(value)
    except (TypeError, ValueError):
        return None
    return n if lo <= n <= hi else None


def get_query(
    mood: Annotated[list[str], Query(max_length=16)] = [],
    genre: Annotated[list[str], Query(max_length=16)] = [],
    runtime: str | None = None,
    max_runtime: str | None = None,
    min_runtime: str | None = None,
    rating: str | None = None,
    year: str | None = None,
    decade: str | None = None,
    language: str | None = None,
) -> RecommendationQuery:
    """Shared by the JSON API and the HTML pages: one vocabulary of query parameters."""
    lo, hi = RUNTIME_PRESETS.get(runtime or "", (None, None))
    min_rt = lo if lo is not None else _num(min_runtime, int, 1, 600)
    max_rt = hi if hi is not None else _num(max_runtime, int, 1, 600)

    year_from = year_to = None
    if (y := _num(year, int, 1888, 2100)) is not None:
        year_from = year_to = y
    elif decade == "pre1970":
        year_to = 1969
    elif (d := _num(decade, int, 1880, 2090)) is not None:
        year_from, year_to = d - d % 10, d - d % 10 + 9

    lang = (language or "").strip().lower()
    return RecommendationQuery(
        moods=_slugs(mood, MAX_MOODS), genres=_slugs(genre, MAX_GENRES),
        min_runtime=min_rt, max_runtime=max_rt, min_rating=_num(rating, float, 0, 10),
        year_from=year_from, year_to=year_to, language=lang if _LANG.match(lang) else None,
    )


@router.get("/recommendations", response_model=RecommendationPageOut)
def recommendations(
    query: RecommendationQuery = Depends(get_query),
    page: int = Query(1, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> RecommendationPageOut:
    res = engine.recommend(db, query, page=page)
    return RecommendationPageOut(
        items=[ScoredMovieOut(**MovieCardOut.from_movie(r.movie).model_dump(), score=r.score) for r in res.items],
        total=res.total, page=res.page, pages=res.pages, relaxed=res.relaxed,
    )
