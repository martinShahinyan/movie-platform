import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Movie
from app.services import movie_service
from scripts.seed import seed_reference_data


def setup_sample_movie(db: Session) -> Movie:
    seed_reference_data(db)
    return movie_service.upsert_from_tmdb(
        db,
        {
            "id": 157336,
            "title": "Interstellar",
            "overview": "A team of explorers travel through a wormhole in space.",
            "poster_path": "/p.jpg",
            "backdrop_path": "/b.jpg",
            "release_date": "2014-11-05",
            "runtime": 169,
            "vote_average": 8.4,
            "vote_count": 100,
            "genres": [{"id": 878, "name": "Sci-Fi"}],
        },
    )


def test_anonymous_cookie_assigned(client: TestClient, db: Session):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "anonymous_id" in resp.cookies


def test_rating_flow(client: TestClient, db: Session):
    movie = setup_sample_movie(db)

    # Submit rating 9
    resp = client.post(f"/api/movies/{movie.id}/rating", json={"value": 9})
    assert resp.status_code == 200
    data = resp.json()
    assert data["value"] == 9

    # Update rating to 10
    resp_update = client.post(f"/api/movies/{movie.id}/rating", json={"value": 10})
    assert resp_update.status_code == 200
    data_update = resp_update.json()
    assert data_update["value"] == 10

    # Get rating stats
    stats_resp = client.get(f"/api/movies/{movie.id}/rating")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["user_rating"] == 10
    assert stats["vote_count"] == 1


def test_log_flow(client: TestClient, db: Session):
    movie = setup_sample_movie(db)

    # Post a log
    resp = client.post(
        f"/api/movies/{movie.id}/log",
        json={
            "rating": 9,
            "text": "Watched at 2 AM. Unreal atmosphere.",
            "watched_at": "2026-10-01",
        },
    )
    assert resp.status_code == 200
    log_data = resp.json()
    assert log_data["text"] == "Watched at 2 AM. Unreal atmosphere."
    assert log_data["rating"] == 9

    # Get movie logs
    list_resp = client.get(f"/api/movies/{movie.id}/logs")
    assert list_resp.status_code == 200
    logs_list = list_resp.json()
    assert len(logs_list) == 1
    assert logs_list[0]["text"] == "Watched at 2 AM. Unreal atmosphere."

    # Get recent global logs
    recent_resp = client.get("/api/logs/recent")
    assert recent_resp.status_code == 200
    recent_list = recent_resp.json()
    assert len(recent_list) >= 1


def test_seo_sitemap_and_robots(client: TestClient, db: Session):
    setup_sample_movie(db)

    sitemap_resp = client.get("/sitemap.xml")
    assert sitemap_resp.status_code == 200
    assert "urlset" in sitemap_resp.text
    assert "/movie/interstellar" in sitemap_resp.text

    robots_resp = client.get("/robots.txt")
    assert robots_resp.status_code == 200
    assert "Sitemap:" in robots_resp.text


def test_admin_auth_and_actions(client: TestClient, db: Session):
    movie = setup_sample_movie(db)

    # Unauthorized access to admin page redirects to login view
    resp = client.get("/admin")
    assert resp.status_code == 200
    assert "Developer Login" in resp.text

    # Login
    login_resp = client.post("/admin/login", data={"password": "admin123"}, follow_redirects=True)
    assert login_resp.status_code == 200
    assert "Movie Catalogue Management" in login_resp.text

    # Delete movie via admin API
    del_resp = client.delete(f"/api/admin/movies/{movie.id}", cookies=login_resp.cookies)
    assert del_resp.status_code == 200
    assert del_resp.json()["status"] == "ok"
