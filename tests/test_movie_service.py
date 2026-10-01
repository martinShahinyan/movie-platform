from datetime import date

from app.models import Movie
from app.services import movie_service
from scripts.seed import seed_reference_data

INTERSTELLAR = {
    "id": 157336, "title": "Interstellar", "original_title": "Interstellar",
    "overview": "A team travels through a wormhole.", "poster_path": "/p.jpg",
    "backdrop_path": "/b.jpg", "release_date": "2014-11-05", "runtime": 169,
    "vote_average": 8.4, "vote_count": 35000, "original_language": "en",
    "genres": [{"id": 878, "name": "Science Fiction"}, {"id": 18, "name": "Drama"},
               {"id": 10751, "name": "Family"}],  # Family is not one of ours -> ignored
}


def test_slugify():
    assert movie_service.slugify("The Shawshank Redemption") == "the-shawshank-redemption"
    assert movie_service.slugify("Amélie") == "amelie"
    assert movie_service.slugify("千と千尋の神隠し") == ""


def test_seed_is_idempotent(db):
    assert seed_reference_data(db) == (16, 13)
    assert seed_reference_data(db) == (0, 0)


def test_upsert_creates_then_updates(db):
    seed_reference_data(db)
    m = movie_service.upsert_from_tmdb(db, INTERSTELLAR)
    assert m.slug == "interstellar"
    assert m.release_date == date(2014, 11, 5)
    assert {g.slug for g in m.genres} == {"sci-fi", "drama"}
    assert 1 <= len(m.moods) <= 4

    # curated moods must survive a re-import
    m.moods = []
    db.commit()
    again = movie_service.upsert_from_tmdb(db, {**INTERSTELLAR, "vote_count": 36000})
    assert again.id == m.id and again.vote_count == 36000 and again.moods == []
    assert db.query(Movie).count() == 1


def test_slug_collision_gets_year(db):
    seed_reference_data(db)
    movie_service.upsert_from_tmdb(db, {"id": 1, "title": "Dune", "release_date": "1984-12-14"})
    m2 = movie_service.upsert_from_tmdb(db, {"id": 2, "title": "Dune", "release_date": "2021-10-22"})
    assert m2.slug == "dune-2021"


def test_non_latin_title_slug_fallback(db):
    m = movie_service.upsert_from_tmdb(db, {"id": 129, "title": "千と千尋の神隠し"})
    assert m.slug == "movie-129"


def test_list_filter_and_pagination(db):
    seed_reference_data(db)
    for i in range(25):
        movie_service.upsert_from_tmdb(db, {
            "id": 1000 + i, "title": f"Film {i}", "release_date": "2020-01-01",
            "vote_count": i, "genres": [{"id": 18, "name": "Drama"}]})
    movie_service.upsert_from_tmdb(db, {"id": 5, "title": "Funny One", "release_date": "2019-05-05",
                                        "genres": [{"id": 35, "name": "Comedy"}]})
    p1 = movie_service.list_movies(db, genre_slug="drama")
    assert (len(p1.items), p1.total, p1.pages) == (20, 25, 2)
    p2 = movie_service.list_movies(db, genre_slug="drama", page=2)
    assert len(p2.items) == 5
    assert movie_service.list_movies(db, year=2019).total == 1
    assert movie_service.list_movies(db, mood_slug="funny").total == 1


def test_search_local_escapes_wildcards(db):
    movie_service.upsert_from_tmdb(db, {"id": 1, "title": "Her"})
    movie_service.upsert_from_tmdb(db, {"id": 2, "title": "Heat"})
    assert [m.title for m in movie_service.search_local(db, "her")] == ["Her"]
    assert movie_service.search_local(db, "%%") == []
    assert movie_service.search_local(db, "h") == []
