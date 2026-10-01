import os

os.environ["DATABASE_URL"] = "sqlite://"  # in-memory DB for tests

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.database import Base, get_db
from app.main import app
from app.services import movie_service
from scripts.seed import seed_reference_data


@pytest.fixture
def db() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(db: Session):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def movies(db: Session):
    """Interstellar + 24 filler dramas, so there are two pages of results."""
    seed_reference_data(db)
    movie_service.upsert_from_tmdb(db, {
        "id": 157336, "title": "Interstellar", "overview": "A team travels through a wormhole.",
        "poster_path": "/p.jpg", "backdrop_path": "/b.jpg", "release_date": "2014-11-05",
        "runtime": 169, "vote_average": 8.4, "vote_count": 99999,
        "genres": [{"id": 878, "name": "Sci-Fi"}, {"id": 18, "name": "Drama"}]})
    for i in range(24):
        movie_service.upsert_from_tmdb(db, {
            "id": 2000 + i, "title": f"Filler {i}", "release_date": "2020-02-02",
            "vote_count": i, "genres": [{"id": 18, "name": "Drama"}]})
