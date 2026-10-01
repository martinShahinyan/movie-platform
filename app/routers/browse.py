"""SEO landing pages (mood / genre / year), hubs, and the 'Find my movie' results page."""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app import content
from app.database import get_db
from app.finder_config import DECADE_OPTIONS, RATING_OPTIONS, RUNTIME_OPTIONS, RUNTIME_PRESETS, label_for, LANGUAGE_OPTIONS
from app.routers.recommendations import get_query
from app.services import movie_service
from app.services import recommendation_service as engine
from app.services.recommendation_service import RecommendationQuery
from app.templating import make_seo, page_url, templates

router = APIRouter(include_in_schema=False)
PageParam = Query(1, ge=1, le=10000)


def _landing(request, db, *, h1, title, description, query, page, intro, faq, related, noindex_if_empty=True):
    # Landing pages list everything that matches; they never "relax" into unrelated movies.
    pg = engine.recommend(db, query, page=page, allow_relax=False)
    if page > pg.pages:
        raise HTTPException(404)
    suffix = f" - Page {page}" if page > 1 else ""
    seo = make_seo(
        request, title=f"{title}{suffix} | Moodreel", description=description,
        params={"page": page}, noindex=noindex_if_empty and pg.total == 0,
    )
    return templates.TemplateResponse(request, "landing.html", {
        "seo": seo, "h1": h1, "pg": pg, "page_url": lambda n: page_url(request, n),
        "intro": intro if page == 1 else (), "faq": faq if page == 1 else (), "related": related,
    })


def _links(items, prefix, skip=None):
    return [(name, f"/{prefix}/{slug}") for name, slug in items if slug != skip]


@router.get("/mood/{slug}")
def mood_page(slug: str, request: Request, page: int = PageParam, db: Session = Depends(get_db)):
    mood = movie_service.get_mood(db, slug)
    if mood is None:
        raise HTTPException(404)
    c = content.mood_content(mood.slug, mood.name)
    related = [
        {"title": "More moods", "links": _links([(m.name, m.slug) for m in movie_service.all_moods(db)], "mood", mood.slug)},
        {"title": "Browse by genre", "links": _links([(g.name, g.slug) for g in movie_service.all_genres(db)], "genre")},
    ]
    return _landing(request, db, h1=f"{mood.name} movies", title=c.title, description=c.description,
                    query=RecommendationQuery(moods=(slug,)), page=page, intro=c.intro, faq=c.faq, related=related)


@router.get("/genre/{slug}")
def genre_page(slug: str, request: Request, page: int = PageParam, db: Session = Depends(get_db)):
    genre = movie_service.get_genre(db, slug)
    if genre is None:
        raise HTTPException(404)
    c = content.genre_content(genre.slug, genre.name)
    related = [
        {"title": "More genres", "links": _links([(g.name, g.slug) for g in movie_service.all_genres(db)], "genre", genre.slug)},
        {"title": "Browse by mood", "links": _links([(m.name, m.slug) for m in movie_service.all_moods(db)], "mood")},
    ]
    return _landing(request, db, h1=f"{genre.name} movies", title=c.title, description=c.description,
                    query=RecommendationQuery(genres=(slug,)), page=page, intro=c.intro, faq=c.faq, related=related)


@router.get("/year/{year}")
def year_page(year: int, request: Request, page: int = PageParam, db: Session = Depends(get_db)):
    years = movie_service.available_years(db)
    count = dict(years).get(year)
    if not count:
        raise HTTPException(404)  # no movies for that year: don't publish a thin page
    related = [{"title": "Other years", "links": [(str(y), f"/year/{y}") for y, _ in years if y != year]}]
    intro = (f"{count} {'movie' if count == 1 else 'movies'} released in {year}, ranked by rating and by how many people have rated them.",)
    return _landing(
        request, db, h1=f"Movies from {year}", title=f"Best Movies of {year}",
        description=f"The best movies released in {year}, ranked by rating, with runtime, genres and mood tags.",
        query=RecommendationQuery(year_from=year, year_to=year), page=page, intro=intro, faq=(), related=related)


def _hub(request, db, *, h1, title, description, rows, prefix, blurbs):
    items = [(name, f"/{prefix}/{slug}", blurbs(slug, name), count) for name, slug, count in rows]
    seo = make_seo(request, title=f"{title} | Moodreel", description=description)
    return templates.TemplateResponse(request, "hub.html", {"seo": seo, "h1": h1, "items": items})


@router.get("/moods")
def moods_hub(request: Request, db: Session = Depends(get_db)):
    rows = [(m.name, m.slug, c) for m, c in movie_service.moods_with_counts(db)]
    return _hub(request, db, h1="Browse movies by mood", title="Movies by mood",
                description="Pick a mood, from sad to mind-bending, and see movies that match how you feel.",
                rows=rows, prefix="mood", blurbs=lambda s, n: content.mood_content(s, n).blurb)


@router.get("/genres")
def genres_hub(request: Request, db: Session = Depends(get_db)):
    rows = [(g.name, g.slug, c) for g, c in movie_service.genres_with_counts(db)]
    return _hub(request, db, h1="Browse movies by genre", title="Movies by genre",
                description="Browse movies by genre, from drama and comedy to sci-fi and horror, ranked by rating.",
                rows=rows, prefix="genre", blurbs=lambda s, n: content.genre_content(s, n).blurb)


@router.get("/find")
def find(
    request: Request,
    query: RecommendationQuery = Depends(get_query),
    page: int = PageParam,
    db: Session = Depends(get_db),
):
    res = engine.recommend(db, query, page=page)
    if page > res.pages:
        raise HTTPException(404)

    moods, genres = movie_service.all_moods(db), movie_service.all_genres(db)
    mood_names = {m.slug: m.name for m in moods}
    genre_names = {g.slug: g.name for g in genres}
    qp = request.query_params
    runtime = qp.get("runtime", "") if qp.get("runtime") in RUNTIME_PRESETS else ""
    decade = qp.get("decade", "") if qp.get("decade") in dict(DECADE_OPTIONS) else ""
    rating = str(int(query.min_rating)) if query.min_rating is not None and query.min_rating == int(query.min_rating) else ""
    sel = {"moods": set(query.moods), "genre": query.genres[0] if query.genres else "",
           "runtime": runtime, "rating": rating, "decade": decade, "language": query.language or ""}

    summary = [mood_names[s] for s in query.moods if s in mood_names]
    summary += [genre_names[s] for s in query.genres if s in genre_names]
    summary += [x for x in (label_for(RUNTIME_OPTIONS, runtime), f"Rated {rating}+" if rating else "",
                            label_for(DECADE_OPTIONS, decade), label_for(LANGUAGE_OPTIONS, sel["language"])) if x]

    seo = make_seo(request, title="Your movie picks | Moodreel",
                   description="Movies matched to your mood.", noindex=True)
    return templates.TemplateResponse(request, "find.html", {
        "seo": seo, "res": res, "summary": summary, "sel": sel, "moods": moods, "genres": genres,
        "page_url": lambda n: page_url(request, n),
    })
