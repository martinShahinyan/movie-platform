import pytest

from app.models import Genre, Movie, Mood
from app.services.recommendation_service import RecommendationQuery as Q, recommend
from scripts.seed import seed_reference_data


def add(db, tmdb_id, title, *, moods=(), genres=(), rating=7.0, votes=1000, runtime=100,
        year=2015, lang="en"):
    from datetime import date
    m = Movie(tmdb_id=tmdb_id, slug=title.lower().replace(" ", "-"), title=title, vote_average=rating,
              vote_count=votes, runtime=runtime, release_date=date(year, 6, 1), original_language=lang)
    m.moods = [db.query(Mood).filter_by(slug=s).one() for s in moods]
    m.genres = [db.query(Genre).filter_by(slug=s).one() for s in genres]
    db.add(m)
    db.commit()
    return m


@pytest.fixture
def catalog(db):
    seed_reference_data(db)
    add(db, 1, "A Both", moods=("sad", "lonely"), genres=("drama",), rating=8.0)
    add(db, 2, "B Sad Only", moods=("sad",), genres=("drama",), rating=7.5)
    add(db, 3, "C Genre Only", genres=("drama",), rating=9.0)
    add(db, 4, "D Unrelated", moods=("funny",), genres=("comedy",), rating=9.5)


def titles(page):
    return [r.movie.title for r in page.items]


def test_score_weights_and_order(catalog, db):
    page = recommend(db, Q(moods=("sad", "lonely"), genres=("drama",)), allow_relax=False)
    assert titles(page) == ["A Both", "B Sad Only", "C Genre Only"]
    assert [r.score for r in page.items] == [13, 8, 3]  # 5+5+3, 5+3, 3
    assert "D Unrelated" not in titles(page)


def test_mood_only_excludes_untagged(catalog, db):
    assert titles(recommend(db, Q(moods=("sad",)), allow_relax=False)) == ["A Both", "B Sad Only"]


def test_hard_filters_when_enough_matches(db):
    seed_reference_data(db)
    for i in range(8):
        add(db, 100 + i, f"Good {i}", moods=("sad",), rating=8.0, runtime=100)
    add(db, 200, "Long Sad", moods=("sad",), rating=8.5, runtime=170)
    add(db, 201, "Low Sad", moods=("sad",), rating=5.0, runtime=100)
    page = recommend(db, Q(moods=("sad",), max_runtime=120, min_rating=7.0))
    assert not page.relaxed and page.total == 8
    assert "Long Sad" not in titles(page) and "Low Sad" not in titles(page)


def test_relaxes_to_closest_matches_when_few(catalog, db):
    page = recommend(db, Q(moods=("sad",), min_rating=8.0))  # strict -> only "A Both" (<6)
    assert page.relaxed and page.total == 2
    assert titles(page)[0] == "A Both"  # still ranked first: 5 + 2 rating bonus
    assert titles(page) == ["A Both", "B Sad Only"]
    assert not recommend(db, Q(moods=("sad",), min_rating=8.0), allow_relax=False).relaxed


def test_decade_language_runtime_null_excluded(db):
    seed_reference_data(db)
    add(db, 1, "Old", moods=("sad",), year=1985)
    add(db, 2, "New", moods=("sad",), year=2021, lang="ko")
    m = add(db, 3, "NoRuntime", moods=("sad",))
    m.runtime = None
    db.commit()
    assert titles(recommend(db, Q(moods=("sad",), year_from=1980, year_to=1989), allow_relax=False)) == ["Old"]
    assert titles(recommend(db, Q(moods=("sad",), language="ko"), allow_relax=False)) == ["New"]
    assert "NoRuntime" not in titles(recommend(db, Q(moods=("sad",), max_runtime=200), allow_relax=False))


def test_pagination_and_tiebreak_discounts_few_votes(db):
    seed_reference_data(db)
    add(db, 1, "Hyped", moods=("sad",), rating=10.0, votes=3)
    for i in range(22):
        add(db, 10 + i, f"Solid {i}", moods=("sad",), rating=7.0, votes=2000)
    p1 = recommend(db, Q(moods=("sad",)), allow_relax=False)
    assert (len(p1.items), p1.total, p1.pages) == (20, 23, 2)
    assert titles(p1)[0] != "Hyped"
    assert len(recommend(db, Q(moods=("sad",)), page=2, allow_relax=False).items) == 3


def test_from_filters_accepts_future_ai_output():
    q = Q.from_filters({"moods": ["lonely", "emotional"], "genres": ["drama"], "intensity": "medium", "runtime": None})
    assert q.moods == ("lonely", "emotional") and q.genres == ("drama",) and q.max_runtime is None
