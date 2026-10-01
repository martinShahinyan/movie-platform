from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Genre, Log, Mood, Movie, Rating
from app.services import log_service, movie_service
from app.services.tmdb_service import TmdbError, TmdbService
from app.templating import make_seo, templates

router = APIRouter(tags=["admin"])
settings = get_settings()

ADMIN_COOKIE_NAME = "admin_auth"


def is_admin(request: Request) -> bool:
    val = request.cookies.get(ADMIN_COOKIE_NAME)
    return val == settings.secret_key


def require_admin(request: Request):
    if not is_admin(request):
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.get("/admin", include_in_schema=False)
def admin_page(request: Request, db: Session = Depends(get_db)):
    authed = is_admin(request)
    seo = make_seo(request, title="Admin Dashboard | Moodreel", description="Admin", noindex=True)

    stats = None
    movies = []
    logs = []
    all_moods = []
    all_genres = []

    if authed:
        movie_count = db.scalar(select(func.count(Movie.id))) or 0
        rating_count = db.scalar(select(func.count(Rating.id))) or 0
        log_count = db.scalar(select(func.count(Log.id))) or 0

        stats = {
            "movie_count": movie_count,
            "rating_count": rating_count,
            "log_count": log_count,
        }
        movies = movie_service.list_movies(db, page=1, per_page=50).items
        logs = log_service.get_recent_logs(db, limit=30)
        all_moods = movie_service.all_moods(db)
        all_genres = movie_service.all_genres(db)

    return templates.TemplateResponse(
        request,
        "admin.html",
        {
            "seo": seo,
            "authed": authed,
            "stats": stats,
            "movies": movies,
            "logs": logs,
            "moods": all_moods,
            "genres": all_genres,
        },
    )


@router.post("/admin/login", include_in_schema=False)
def admin_login(
    password: Annotated[str, Form()],
    response: Response,
):
    if password == settings.admin_password or (not settings.admin_password and password == "admin123"):
        resp = RedirectResponse("/admin", status_code=303)
        resp.set_cookie(key=ADMIN_COOKIE_NAME, value=settings.secret_key, httponly=True, samesite="lax")
        return resp
    return RedirectResponse("/admin?error=invalid_password", status_code=303)


@router.get("/admin/logout", include_in_schema=False)
def admin_logout(response: Response):
    resp = RedirectResponse("/admin", status_code=303)
    resp.delete_cookie(ADMIN_COOKIE_NAME)
    return resp


class ImportMovieRequest(BaseModel):
    tmdb_id: int


class MoodsUpdateRequest(BaseModel):
    mood_slugs: list[str]


class GenresUpdateRequest(BaseModel):
    genre_slugs: list[str]


@router.post("/api/admin/movies/import")
def admin_import_movie(
    payload: ImportMovieRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    require_admin(request)
    try:
        tmdb = TmdbService()
        movie = tmdb.import_movie(db, payload.tmdb_id)
        tmdb.close()
        return {"status": "ok", "movie_id": movie.id, "slug": movie.slug, "title": movie.title}
    except TmdbError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/api/admin/movies/{movie_id}/moods")
def admin_update_movie_moods(
    movie_id: int,
    payload: MoodsUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    require_admin(request)
    movie = db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    moods = list(db.scalars(select(Mood).where(Mood.slug.in_(payload.mood_slugs))).all())
    movie.moods = moods
    db.commit()
    return {"status": "ok", "moods": [m.name for m in movie.moods]}


@router.post("/api/admin/movies/{movie_id}/genres")
def admin_update_movie_genres(
    movie_id: int,
    payload: GenresUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    require_admin(request)
    movie = db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    genres = list(db.scalars(select(Genre).where(Genre.slug.in_(payload.genre_slugs))).all())
    movie.genres = genres
    db.commit()
    return {"status": "ok", "genres": [g.name for g in movie.genres]}


@router.delete("/api/admin/logs/{log_id}")
def admin_delete_log(
    log_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    require_admin(request)
    success = log_service.delete_log(db, log_id)
    if not success:
        raise HTTPException(status_code=404, detail="Log not found")
    return {"status": "ok"}


@router.delete("/api/admin/movies/{movie_id}")
def admin_delete_movie(
    movie_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    require_admin(request)
    movie = db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    db.delete(movie)
    db.commit()
    return {"status": "ok"}
