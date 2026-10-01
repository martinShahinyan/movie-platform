from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.anonymous import get_anonymous_id
from app.models import Movie
from app.schemas.log import LogCreate, LogOut
from app.services import log_service, rating_service
from app.services.tmdb_service import image_url

router = APIRouter(prefix="/api", tags=["logs"])


@router.post("/movies/{movie_id}/log", response_model=LogOut)
def create_movie_log(
    movie_id: int,
    payload: LogCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> LogOut:
    movie = db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    anonymous_id = get_anonymous_id(request)

    # If log payload contains a rating, sync/upsert user's rating too
    if payload.rating:
        rating_service.upsert_rating(
            db, movie_id=movie_id, anonymous_id=anonymous_id, value=payload.rating
        )

    log_entry = log_service.create_log(
        db,
        movie_id=movie_id,
        anonymous_id=anonymous_id,
        text=payload.text,
        rating=payload.rating,
        watched_at=payload.watched_at,
    )

    out = LogOut.model_validate(log_entry)
    out.movie_title = movie.title
    out.movie_slug = movie.slug
    out.poster_path = image_url(movie.poster_path, "w185")
    return out


@router.get("/movies/{movie_id}/logs", response_model=list[LogOut])
def get_movie_logs(
    movie_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[LogOut]:
    movie = db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    logs = log_service.get_movie_logs(db, movie_id=movie_id, limit=limit)
    res = []
    for l in logs:
        item = LogOut.model_validate(l)
        item.movie_title = movie.title
        item.movie_slug = movie.slug
        item.poster_path = image_url(movie.poster_path, "w185")
        res.append(item)
    return res


@router.get("/logs/recent", response_model=list[LogOut])
def get_recent_logs(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[LogOut]:
    logs = log_service.get_recent_logs(db, limit=limit)
    res = []
    for l in logs:
        item = LogOut.model_validate(l)
        if l.movie:
            item.movie_title = l.movie.title
            item.movie_slug = l.movie.slug
            item.poster_path = image_url(l.movie.poster_path, "w185")
        res.append(item)
    return res
