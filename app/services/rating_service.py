from __future__ import annotations

import uuid
from typing import Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Movie, Rating


def get_user_rating(db: Session, movie_id: int, anonymous_id: uuid.UUID) -> Rating | None:
    return db.scalar(
        select(Rating).where(
            Rating.movie_id == movie_id,
            Rating.anonymous_id == anonymous_id,
        )
    )


def upsert_rating(
    db: Session, movie_id: int, anonymous_id: uuid.UUID, value: int
) -> Tuple[Rating, float, int]:
    rating = get_user_rating(db, movie_id, anonymous_id)
    if rating:
        rating.value = value
    else:
        rating = Rating(movie_id=movie_id, anonymous_id=anonymous_id, value=value)
        db.add(rating)
    db.flush()

    # Recalculate average rating and count for this movie
    movie = db.get(Movie, movie_id)
    if movie:
        stats = db.execute(
            select(func.avg(Rating.value), func.count(Rating.id)).where(
                Rating.movie_id == movie_id
            )
        ).one()
        avg_val, count_val = stats[0], stats[1]
        if avg_val is not None and count_val > 0:
            movie.vote_average = round(float(avg_val), 1)
            movie.vote_count = count_val

    db.commit()
    db.refresh(rating)
    if movie:
        db.refresh(movie)
        avg = movie.vote_average
        cnt = movie.vote_count
    else:
        avg, cnt = float(value), 1

    return rating, avg, cnt
