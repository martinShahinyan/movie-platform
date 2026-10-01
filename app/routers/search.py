from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.movie import SearchHitOut
from app.services import movie_service
from app.services.tmdb_service import image_url

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search", response_model=list[SearchHitOut])
def search(
    q: str = Query("", max_length=100),
    limit: int = Query(8, ge=1, le=20),
    db: Session = Depends(get_db),
) -> list[SearchHitOut]:
    """Autocomplete. Searches our own database only (never TMDB)."""
    return [
        SearchHitOut(slug=m.slug, title=m.title, year=m.year, poster_url=image_url(m.poster_path, "w92"))
        for m in movie_service.search_local(db, q, limit=limit)
    ]
