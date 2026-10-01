import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.anonymous import get_anonymous_id
from app.models import Movie
from app.schemas.rating import MovieRatingStatsOut, RatingCreate, RatingOut
from app.services import rating_service

router = APIRouter(prefix="/api/movies", tags=["ratings"])


@router.post("/{movie_id}/rating", response_model=RatingOut)
@router.put("/{movie_id}/rating", response_model=RatingOut)
def rate_movie(
    movie_id: int,
    payload: RatingCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> RatingOut:
    movie = db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    anonymous_id = get_anonymous_id(request)
    rating, _, _ = rating_service.upsert_rating(
        db, movie_id=movie_id, anonymous_id=anonymous_id, value=payload.value
    )
    return rating


@router.get("/{movie_id}/rating", response_model=MovieRatingStatsOut)
def get_movie_rating(
    movie_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> MovieRatingStatsOut:
    movie = db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    anonymous_id = get_anonymous_id(request)
    user_rating_obj = rating_service.get_user_rating(db, movie_id, anonymous_id)
    user_rating = user_rating_obj.value if user_rating_obj else None

    return MovieRatingStatsOut(
        user_rating=user_rating,
        community_rating=round(movie.vote_average, 1),
        vote_count=movie.vote_count,
    )
