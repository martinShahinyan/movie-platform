import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Request, Response
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.database import Base, engine, get_db
from app.dependencies.anonymous import COOKIE_NAME, get_anonymous_id, set_anonymous_id_cookie
from app.routers import admin, browse, genres, logs, moods, movies, pages, ratings, recommendations, search, seo
from app.templating import make_seo, templates

BASE_DIR = Path(__file__).resolve().parent
settings = get_settings()
log = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO if settings.is_production else logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist on startup (safely handled if already created by another worker)
    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
    except Exception as e:
        log.warning("Table creation skipped or already exists: %s", e)
    try:
        from app.database import SessionLocal
        from scripts.seed import seed_reference_data, seed_starter_movies
        with SessionLocal() as db:
            seed_reference_data(db)
            seed_starter_movies(db)
    except Exception as e:
        log.warning("Seed on startup skipped or failed: %s", e)
    yield


app = FastAPI(
    title="Moodreel",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.middleware("http")
async def ensure_anonymous_cookie(request: Request, call_next):
    anonymous_id = get_anonymous_id(request)
    response: Response = await call_next(request)
    if COOKIE_NAME not in request.cookies:
        set_anonymous_id_cookie(response, anonymous_id)
    return response


app.include_router(pages.router)
app.include_router(browse.router)
app.include_router(movies.router)
app.include_router(search.router)
app.include_router(recommendations.router)
app.include_router(moods.router)
app.include_router(genres.router)
app.include_router(ratings.router)
app.include_router(logs.router)
app.include_router(admin.router)
app.include_router(seo.router)


def _not_found(request: Request):
    seo = make_seo(request, title="Page not found | Moodreel", description="Page not found.", noindex=True)
    return templates.TemplateResponse(request, "404.html", {"seo": seo}, status_code=404)


@app.exception_handler(StarletteHTTPException)
async def on_http_error(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404 and not request.url.path.startswith("/api"):
        return _not_found(request)
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def on_validation_error(request: Request, exc: RequestValidationError):
    if not request.url.path.startswith("/api"):
        return _not_found(request)
    return await request_validation_exception_handler(request, exc)


@app.exception_handler(Exception)
async def on_server_error(request: Request, exc: Exception):
    log.exception("Unhandled error on %s", request.url.path)
    from fastapi.responses import JSONResponse

    if request.url.path.startswith("/api"):
        return JSONResponse({"detail": "Internal server error"}, status_code=500)
    seo = make_seo(request, title="Something went wrong | Moodreel", description="Error.", noindex=True)
    return templates.TemplateResponse(request, "500.html", {"seo": seo}, status_code=500)


@app.get("/health", include_in_schema=False)
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
