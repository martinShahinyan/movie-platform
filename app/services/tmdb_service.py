"""TMDB client. Used for import/refresh only - never on a page request."""
from __future__ import annotations

import logging
import time
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Movie
from app.services import movie_service

log = logging.getLogger(__name__)

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p"


class TmdbError(RuntimeError):
    pass


def image_url(path: str | None, size: str = "w500") -> str | None:
    if not path:
        return None
    if path.startswith("http://") or path.startswith("https://") or path.startswith("/static/"):
        return path
    return f"{IMAGE_BASE}/{size}{path}"


class TmdbService:
    def __init__(self, api_key: str | None = None, client: httpx.Client | None = None,
                 request_delay: float = 0.1) -> None:
        key = api_key if api_key is not None else get_settings().tmdb_api_key
        if not key:
            raise TmdbError("TMDB_API_KEY is not set (see .env.example)")
        headers: dict[str, str] = {}
        self._params: dict[str, str] = {}
        if key.startswith("eyJ"):  # v4 read-access token (JWT)
            headers["Authorization"] = f"Bearer {key}"
        else:                      # v3 API key
            self._params["api_key"] = key
        self._client = client or httpx.Client(base_url=BASE_URL, headers=headers, timeout=10.0)
        self._delay = request_delay

    def _get(self, path: str, **params: Any) -> dict[str, Any]:
        time.sleep(self._delay)
        try:
            resp = self._client.get(path, params={**self._params, **params})
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise TmdbError(f"TMDB request failed for {path}: {exc}") from exc
        return resp.json()

    # --- raw API ---
    def search_movies(self, query: str, page: int = 1) -> list[dict[str, Any]]:
        return self._get("/search/movie", query=query, page=page, include_adult="false")["results"]

    def get_popular_movies(self, page: int = 1) -> list[dict[str, Any]]:
        return self._get("/movie/popular", page=page)["results"]

    def get_top_rated_movies(self, page: int = 1) -> list[dict[str, Any]]:
        return self._get("/movie/top_rated", page=page)["results"]

    def get_movie(self, tmdb_id: int) -> dict[str, Any]:
        """Basic movie payload (same endpoint as details; kept for API symmetry)."""
        return self._get(f"/movie/{tmdb_id}")

    def get_movie_details(self, tmdb_id: int) -> dict[str, Any]:
        return self.get_movie(tmdb_id)

    # --- import ---
    def import_movie(self, db: Session, tmdb_id: int) -> Movie:
        """Fetch full details (runtime + genres) and upsert into PostgreSQL."""
        return movie_service.upsert_from_tmdb(db, self.get_movie_details(tmdb_id))

    def close(self) -> None:
        self._client.close()
