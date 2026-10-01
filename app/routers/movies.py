from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.movie import MovieDetailOut, MoviePageOut, MovieCardOut
from app.services import movie_service

router = APIRouter(prefix="/api/movies", tags=["movies"])

SLUG_RE = r"^[a-z0-9-]{1,60}$"


@router.get("", response_model=MoviePageOut)
def list_movies(
    page: int = Query(1, ge=1, le=10000),
    genre: str | None = Query(None, pattern=SLUG_RE),
    mood: str | None = Query(None, pattern=SLUG_RE),
    year: int | None = Query(None, ge=1888, le=2100),
    db: Session = Depends(get_db),
) -> MoviePageOut:
    pg = movie_service.list_movies(db, page=page, genre_slug=genre, mood_slug=mood, year=year)
    return MoviePageOut(
        items=[MovieCardOut.from_movie(m) for m in pg.items],
        total=pg.total, page=pg.page, pages=pg.pages,
    )


@router.get("/{slug}", response_model=MovieDetailOut)
def get_movie(slug: str, db: Session = Depends(get_db)) -> MovieDetailOut:
    movie = movie_service.get_by_slug(db, slug)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return MovieDetailOut.from_movie(movie)
