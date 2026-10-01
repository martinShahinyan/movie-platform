import httpx
import pytest

from app.services.tmdb_service import TmdbError, TmdbService, image_url
from scripts.seed import seed_reference_data


def make_service(handler, key="abc123") -> TmdbService:
    client = httpx.Client(base_url="https://api.themoviedb.org/3", transport=httpx.MockTransport(handler))
    return TmdbService(api_key=key, client=client, request_delay=0)


def test_missing_key_raises():
    with pytest.raises(TmdbError):
        TmdbService(api_key="")


def test_v3_key_sent_as_query_param():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["params"] = dict(request.url.params)
        return httpx.Response(200, json={"results": [{"id": 1}]})

    assert make_service(handler).get_popular_movies(2) == [{"id": 1}]
    assert seen["params"] == {"api_key": "abc123", "page": "2"}


def test_import_movie_end_to_end(db):
    seed_reference_data(db)

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/3/movie/603"
        return httpx.Response(200, json={
            "id": 603, "title": "The Matrix", "release_date": "1999-03-30", "runtime": 136,
            "vote_average": 8.2, "vote_count": 25000,
            "genres": [{"id": 28, "name": "Action"}, {"id": 878, "name": "Sci-Fi"}]})

    movie = make_service(handler).import_movie(db, 603)
    assert movie.slug == "the-matrix" and movie.runtime == 136
    assert {g.slug for g in movie.genres} == {"action", "sci-fi"}


def test_http_error_wrapped():
    svc = make_service(lambda r: httpx.Response(401, json={"status_message": "Invalid API key"}))
    with pytest.raises(TmdbError):
        svc.get_movie(1)


def test_image_url():
    assert image_url("/a.jpg") == "https://image.tmdb.org/t/p/w500/a.jpg"
    assert image_url(None) is None
