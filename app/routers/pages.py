"""Core server-rendered pages. Business logic lives in services/."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.content import HOME_MOOD_TILES
from app.database import get_db
from app.dependencies.anonymous import get_anonymous_id
from app.routers.movies import SLUG_RE
from app.services import log_service, movie_service, rating_service
from app.services.tmdb_service import image_url
from app.templating import make_seo, page_url, templates

router = APIRouter(include_in_schema=False)


@router.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    popular = movie_service.list_movies(db, per_page=10).items
    recent_logs = log_service.get_recent_logs(db, limit=6)
    seo = make_seo(
        request,
        title="Moodreel - find a movie that matches your mood",
        description="Tell us how you feel and find a movie to match. Rate and log what you watch, anonymously, no account needed.",
    )
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "seo": seo,
            "popular": popular,
            "recent_logs": recent_logs,
            "moods": movie_service.all_moods(db),
            "genres": movie_service.all_genres(db),
            "sel": {"moods": set(), "genre": "", "runtime": "", "rating": "7", "decade": "", "language": ""},
            "mood_tiles": HOME_MOOD_TILES,
        },
    )


@router.get("/movies")
def movies(
    request: Request,
    page: int = Query(1, ge=1, le=10000),
    genre: str | None = Query(None, pattern=SLUG_RE),
    mood: str | None = Query(None, pattern=SLUG_RE),
    year: int | None = Query(None, ge=1888, le=2100),
    db: Session = Depends(get_db),
):
    genre_obj = movie_service.get_genre(db, genre) if genre else None
    mood_obj = movie_service.get_mood(db, mood) if mood else None
    if (genre and not genre_obj) or (mood and not mood_obj):
        raise HTTPException(404)

    # A single filter has a proper landing page: send visitors (and crawlers) there.
    if sum(bool(x) for x in (genre, mood, year)) == 1:
        target = f"/genre/{genre}" if genre else f"/mood/{mood}" if mood else f"/year/{year}"
        return RedirectResponse(target + (f"?page={page}" if page > 1 else ""), status_code=301)

    pg = movie_service.list_movies(db, page=page, genre_slug=genre, mood_slug=mood, year=year)
    if page > pg.pages:
        raise HTTPException(404)

    parts = [x.name for x in (mood_obj, genre_obj) if x]
    heading = f"{' '.join(parts)} movies" if parts else "All movies"
    if year:
        heading += f" from {year}"
    seo = make_seo(
        request,
        title=f"{heading} | Moodreel",
        description=f"{heading} to watch tonight, with ratings, runtime and mood tags.",
        params={"page": page, "genre": genre, "mood": mood, "year": year},
        noindex=bool(genre or mood or year),  # combined filters are not landing pages
    )
    return templates.TemplateResponse(
        request,
        "movies.html",
        {
            "seo": seo,
            "heading": heading,
            "pg": pg,
            "filtered": bool(genre or mood or year),
            "page_url": lambda n: page_url(request, n),
        },
    )


@router.get("/movie/{slug}")
def movie_page(slug: str, request: Request, db: Session = Depends(get_db)):
    movie = movie_service.get_by_slug(db, slug)
    if movie is None:
        raise HTTPException(404)
    year = f" ({movie.year})" if movie.year else ""

    anonymous_id = get_anonymous_id(request)
    user_rating_obj = rating_service.get_user_rating(db, movie.id, anonymous_id)
    user_rating = user_rating_obj.value if user_rating_obj else None
    logs = log_service.get_movie_logs(db, movie.id, limit=20)

    seo = make_seo(
        request,
        title=f"{movie.title}{year} | Moodreel",
        description=movie.overview or f"{movie.title}: ratings, mood tags and anonymous viewer logs.",
        image=image_url(movie.backdrop_path or movie.poster_path, "w780"),
        og_type="video.movie",
    )
    return templates.TemplateResponse(
        request,
        "movie.html",
        {
            "seo": seo,
            "movie": movie,
            "user_rating": user_rating,
            "logs": logs,
        },
    )


@router.get("/search")
def search_page(request: Request, q: str = Query("", max_length=100), db: Session = Depends(get_db)):
    q = q.strip()
    results = movie_service.search_local(db, q, limit=40)
    seo = make_seo(
        request,
        title=f"Search results for \u201c{q}\u201d | Moodreel" if q else "Search | Moodreel",
        description="Search movies on Moodreel.",
        noindex=True,  # internal search results should not be indexed
    )
    return templates.TemplateResponse(
        request,
        "search.html",
        {
            "seo": seo,
            "q": q,
            "results": results,
        },
    )
