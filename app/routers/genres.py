from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.movie import TaxonomyOut
from app.services import movie_service

router = APIRouter(prefix="/api", tags=["genres"])


@router.get("/genres", response_model=list[TaxonomyOut])
def list_genres(db: Session = Depends(get_db)) -> list[TaxonomyOut]:
    return [TaxonomyOut(name=g.name, slug=g.slug, movie_count=c) for g, c in movie_service.genres_with_counts(db)]
