from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.movie import TaxonomyOut
from app.services import movie_service

router = APIRouter(prefix="/api", tags=["moods"])


@router.get("/moods", response_model=list[TaxonomyOut])
def list_moods(db: Session = Depends(get_db)) -> list[TaxonomyOut]:
    return [TaxonomyOut(name=m.name, slug=m.slug, movie_count=c) for m, c in movie_service.moods_with_counts(db)]
