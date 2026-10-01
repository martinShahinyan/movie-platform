import uuid
from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Genre, Log, Movie, Mood, Rating


def make_movie(**kw) -> Movie:
    defaults = dict(tmdb_id=157336, slug="interstellar", title="Interstellar",
                    release_date=date(2014, 11, 5), runtime=169, vote_average=8.4)
    return Movie(**{**defaults, **kw})


def test_movie_with_genres_and_moods(db):
    m = make_movie(genres=[Genre(name="Sci-Fi", slug="sci-fi")],
                   moods=[Mood(name="Atmospheric", slug="atmospheric")])
    db.add(m)
    db.commit()
    assert m.year == 2014
    assert [g.slug for g in m.genres] == ["sci-fi"]
    assert [x.slug for x in m.moods] == ["atmospheric"]


def test_slug_and_tmdb_id_unique(db):
    db.add(make_movie())
    db.commit()
    db.add(make_movie(tmdb_id=1))  # same slug
    with pytest.raises(IntegrityError):
        db.commit()


def test_one_rating_per_anonymous_user(db):
    m = make_movie()
    db.add(m)
    db.commit()
    anon = uuid.uuid4()
    db.add(Rating(movie_id=m.id, anonymous_id=anon, value=9))
    db.commit()
    db.add(Rating(movie_id=m.id, anonymous_id=anon, value=5))
    with pytest.raises(IntegrityError):
        db.commit()


def test_rating_range_enforced(db):
    m = make_movie()
    db.add(m)
    db.commit()
    db.add(Rating(movie_id=m.id, anonymous_id=uuid.uuid4(), value=11))
    with pytest.raises(IntegrityError):
        db.commit()


def test_log_saved(db):
    m = make_movie()
    db.add(m)
    db.commit()
    db.add(Log(movie_id=m.id, anonymous_id=uuid.uuid4(), rating=9, text="Watched at 2 AM."))
    db.commit()
    assert db.query(Log).count() == 1
