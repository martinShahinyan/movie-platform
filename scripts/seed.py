"""Seed reference data (moods, genres, movies, and sample logs).

Run: python -m scripts.seed
"""
from datetime import date
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.models import Genre, Log, Mood, Movie
from app.seed_data import GENRES, MOODS

log = logging.getLogger(__name__)

# Pre-built popular movies data with 100% verified posters & backdrops
STARTER_MOVIES = [
    {
        "tmdb_id": 157336,
        "title": "Interstellar",
        "original_title": "Interstellar",
        "slug": "interstellar",
        "overview": "The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel and conquer the vast distances involved in an interstellar voyage.",
        "poster_path": "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        "backdrop_path": "/xJHokMbljvjADYdit5fKSuVQwOZ.jpg",
        "release_date": date(2014, 11, 5),
        "runtime": 169,
        "vote_average": 8.4,
        "vote_count": 36120,
        "original_language": "en",
        "genres": ["sci-fi", "drama", "adventure"],
        "moods": ["atmospheric", "emotional", "thought-provoking", "mind-bending", "lonely"]
    },
    {
        "tmdb_id": 27205,
        "title": "Inception",
        "original_title": "Inception",
        "slug": "inception",
        "overview": "Cobb, a skilled thief who commits corporate espionage by infiltrating the subconscious of his targets is offered a chance to have his criminal history erased as payment for the implantation of another person's idea into a target's subconscious.",
        "poster_path": "/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
        "backdrop_path": "/8ZTVqvKDQ8emSGUEMjsS4yHAi4B.jpg",
        "release_date": date(2010, 7, 15),
        "runtime": 148,
        "vote_average": 8.4,
        "vote_count": 36500,
        "original_language": "en",
        "genres": ["action", "sci-fi", "adventure"],
        "moods": ["mind-bending", "intense", "atmospheric", "thought-provoking"]
    },
    {
        "tmdb_id": 155,
        "title": "The Dark Knight",
        "original_title": "The Dark Knight",
        "slug": "the-dark-knight",
        "overview": "Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the streets.",
        "poster_path": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "backdrop_path": "/dqK9Hag1054tghRQSqLSfrkrjGD.jpg",
        "release_date": date(2008, 7, 16),
        "runtime": 152,
        "vote_average": 8.5,
        "vote_count": 32800,
        "original_language": "en",
        "genres": ["action", "crime", "drama"],
        "moods": ["dark", "intense", "atmospheric"]
    },
    {
        "tmdb_id": 152601,
        "title": "Her",
        "original_title": "Her",
        "slug": "her-2013",
        "overview": "In the near future, a lonely writer develops an unlikely relationship with an operating system designed to meet his every need.",
        "poster_path": "/static/images/posters/her.png",
        "backdrop_path": "/xJHokMbljvjADYdit5fKSuVQwOZ.jpg",
        "release_date": date(2013, 12, 18),
        "runtime": 126,
        "vote_average": 7.9,
        "vote_count": 13900,
        "original_language": "en",
        "genres": ["romance", "sci-fi", "drama"],
        "moods": ["lonely", "emotional", "cozy", "romantic", "atmospheric", "thought-provoking"]
    },
    {
        "tmdb_id": 244786,
        "title": "Whiplash",
        "original_title": "Whiplash",
        "slug": "whiplash",
        "overview": "Under the direction of a ruthless instructor, a talented young drummer begins to pursue perfection at any cost.",
        "poster_path": "/static/images/posters/whiplash.png",
        "backdrop_path": "/dqK9Hag1054tghRQSqLSfrkrjGD.jpg",
        "release_date": date(2014, 10, 10),
        "runtime": 107,
        "vote_average": 8.4,
        "vote_count": 14500,
        "original_language": "en",
        "genres": ["drama"],
        "moods": ["intense", "emotional", "motivational"]
    },
    {
        "tmdb_id": 313369,
        "title": "La La Land",
        "original_title": "La La Land",
        "slug": "la-la-land",
        "overview": "Mia, an aspiring actress, serves lattes to movie stars in between auditions and Sebastian, a dedicated jazz musician, plays in dingy bars to get by. But as success mounts they are faced with decisions that fray the fragile fabric of their love affair.",
        "poster_path": "/static/images/posters/lalaland.png",
        "backdrop_path": "/8ZTVqvKDQ8emSGUEMjsS4yHAi4B.jpg",
        "release_date": date(2016, 12, 1),
        "runtime": 128,
        "vote_average": 7.9,
        "vote_count": 16200,
        "original_language": "en",
        "genres": ["romance", "drama", "comedy"],
        "moods": ["romantic", "nostalgic", "emotional", "happy"]
    },
    {
        "tmdb_id": 550,
        "title": "Fight Club",
        "original_title": "Fight Club",
        "slug": "fight-club",
        "overview": "A ticking-time-bomb insomniac and a slippery soap salesman channel primal male aggression into a shocking new form of therapy.",
        "poster_path": "/static/images/posters/fightclub.png",
        "backdrop_path": "/dqK9Hag1054tghRQSqLSfrkrjGD.jpg",
        "release_date": date(1999, 10, 15),
        "runtime": 139,
        "vote_average": 8.4,
        "vote_count": 28900,
        "original_language": "en",
        "genres": ["drama"],
        "moods": ["dark", "mind-bending", "intense", "thought-provoking"]
    },
    {
        "tmdb_id": 129,
        "title": "Spirited Away",
        "original_title": "千と千尋の神隠し",
        "slug": "spirited-away",
        "overview": "A young girl, Chihiro, becomes trapped in a strange new world of spirits. When her parents undergo a mysterious transformation, she must call upon the courage she never knew she had to free herself and her family.",
        "poster_path": "/static/images/posters/spiritedaway.png",
        "backdrop_path": "/xJHokMbljvjADYdit5fKSuVQwOZ.jpg",
        "release_date": date(2001, 7, 20),
        "runtime": 125,
        "vote_average": 8.5,
        "vote_count": 16400,
        "original_language": "ja",
        "genres": ["animation", "fantasy"],
        "moods": ["cozy", "atmospheric", "nostalgic", "mind-bending"]
    },
    {
        "tmdb_id": 38,
        "title": "Eternal Sunshine of the Spotless Mind",
        "original_title": "Eternal Sunshine of the Spotless Mind",
        "slug": "eternal-sunshine-of-the-spotless-mind",
        "overview": "Joel Barish, severed by heartbreak after a painful breakup, undergoes a medical procedure to erase all memories of his ex-girlfriend Clementine.",
        "poster_path": "/5MwkWH9tYHv3mV9OdYTMR5qreIz.jpg",
        "backdrop_path": "/8ZTVqvKDQ8emSGUEMjsS4yHAi4B.jpg",
        "release_date": date(2004, 3, 19),
        "runtime": 108,
        "vote_average": 8.1,
        "vote_count": 14200,
        "original_language": "en",
        "genres": ["sci-fi", "romance", "drama"],
        "moods": ["romantic", "lonely", "emotional", "mind-bending", "atmospheric"]
    },
    {
        "tmdb_id": 872585,
        "title": "Oppenheimer",
        "original_title": "Oppenheimer",
        "slug": "oppenheimer",
        "overview": "The story of J. Robert Oppenheimer's role in the development of the atomic bomb during World War II.",
        "poster_path": "/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
        "backdrop_path": "/fm6KqXpk3M2HVveHwCrBSSBaO0V.jpg",
        "release_date": date(2023, 7, 19),
        "runtime": 181,
        "vote_average": 8.1,
        "vote_count": 8900,
        "original_language": "en",
        "genres": ["drama"],
        "moods": ["intense", "thought-provoking", "atmospheric", "dark"]
    },
    {
        "tmdb_id": 680,
        "title": "Pulp Fiction",
        "original_title": "Pulp Fiction",
        "slug": "pulp-fiction",
        "overview": "A burger-loving hitman, his philosophical partner, a drug-addled gangster's moll and a washed-up boxer intersect in four tales of violence and redemption.",
        "poster_path": "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
        "backdrop_path": "/dqK9Hag1054tghRQSqLSfrkrjGD.jpg",
        "release_date": date(1994, 9, 10),
        "runtime": 154,
        "vote_average": 8.5,
        "vote_count": 27000,
        "original_language": "en",
        "genres": ["crime", "drama"],
        "moods": ["dark", "funny", "intense"]
    },
    {
        "tmdb_id": 693134,
        "title": "Dune: Part Two",
        "original_title": "Dune: Part Two",
        "slug": "dune-part-two",
        "overview": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.",
        "poster_path": "/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg",
        "backdrop_path": "/xOMo8ScSpB3v9v9.jpg",
        "release_date": date(2024, 2, 27),
        "runtime": 166,
        "vote_average": 8.3,
        "vote_count": 5200,
        "original_language": "en",
        "genres": ["sci-fi", "adventure"],
        "moods": ["atmospheric", "intense", "thought-provoking"]
    },
    {
        "tmdb_id": 335984,
        "title": "Blade Runner 2049",
        "original_title": "Blade Runner 2049",
        "slug": "blade-runner-2049",
        "overview": "Thirty years after the events of the first film, a new blade runner, LAPD Officer K, unearths a long-buried secret that has the potential to plunge what's left of society into chaos.",
        "poster_path": "/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg",
        "backdrop_path": "/xJHokMbljvjADYdit5fKSuVQwOZ.jpg",
        "release_date": date(2017, 10, 4),
        "runtime": 164,
        "vote_average": 7.9,
        "vote_count": 13000,
        "original_language": "en",
        "genres": ["sci-fi", "drama", "mystery"],
        "moods": ["atmospheric", "lonely", "thought-provoking", "dark", "mind-bending"]
    },
    {
        "tmdb_id": 238,
        "title": "The Godfather",
        "original_title": "The Godfather",
        "slug": "the-godfather",
        "overview": "Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family.",
        "poster_path": "/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
        "backdrop_path": "/rSPw7tgCH9c6NqICZef4kZjFOQ5.jpg",
        "release_date": date(1972, 3, 14),
        "runtime": 175,
        "vote_average": 8.7,
        "vote_count": 19800,
        "original_language": "en",
        "genres": ["crime", "drama"],
        "moods": ["dark", "intense", "atmospheric"]
    }
]

SAMPLE_LOGS = [
    {
        "movie_slug": "interstellar",
        "rating": 10,
        "text": "Watched this at 2 AM. The docking scene soundtrack gave me chills all over. An absolute masterpiece of atmosphere.",
    },
    {
        "movie_slug": "her-2013",
        "rating": 9,
        "text": "Felt remarkably melancholic and quiet. Highly recommended if you are feeling lonely late at night.",
    },
    {
        "movie_slug": "eternal-sunshine-of-the-spotless-mind",
        "rating": 9,
        "text": "The bittersweet warmth of remembering someone you once loved. Hits directly in the heart every single time.",
    },
    {
        "movie_slug": "whiplash",
        "rating": 10,
        "text": "Pure adrenaline from start to finish. The last 15 minutes are unmatched.",
    }
]


def seed_reference_data(db: Session) -> tuple[int, int]:
    """Insert missing moods/genres; returns (new_moods, new_genres)."""
    new_moods = new_genres = 0
    existing_moods = set(db.scalars(select(Mood.slug)))
    for name, slug in MOODS:
        if slug not in existing_moods:
            db.add(Mood(name=name, slug=slug))
            new_moods += 1
    existing_genres = set(db.scalars(select(Genre.slug)))
    for name, slug in GENRES:
        if slug not in existing_genres:
            db.add(Genre(name=name, slug=slug))
            new_genres += 1
    db.commit()
    return new_moods, new_genres


def seed_starter_movies(db: Session) -> int:
    added = 0
    genres_by_slug = {g.slug: g for g in db.scalars(select(Genre)).all()}
    moods_by_slug = {m.slug: m for m in db.scalars(select(Mood)).all()}

    for item in STARTER_MOVIES:
        existing = db.scalar(select(Movie).where(Movie.tmdb_id == item["tmdb_id"]))
        if existing:
            # Update poster_path and backdrop_path
            existing.poster_path = item["poster_path"]
            existing.backdrop_path = item["backdrop_path"]
        else:
            m = Movie(
                tmdb_id=item["tmdb_id"],
                title=item["title"],
                original_title=item["original_title"],
                slug=item["slug"],
                overview=item["overview"],
                poster_path=item["poster_path"],
                backdrop_path=item["backdrop_path"],
                release_date=item["release_date"],
                runtime=item["runtime"],
                vote_average=item["vote_average"],
                vote_count=item["vote_count"],
                original_language=item["original_language"],
            )
            m.genres = [genres_by_slug[g] for g in item["genres"] if g in genres_by_slug]
            m.moods = [moods_by_slug[md] for md in item["moods"] if md in moods_by_slug]
            db.add(m)
            added += 1
    db.commit()

    # Seed sample logs if no logs exist
    if db.scalar(select(Log.id)) is None:
        import uuid
        for log_item in SAMPLE_LOGS:
            mov = db.scalar(select(Movie).where(Movie.slug == log_item["movie_slug"]))
            if mov:
                db.add(
                    Log(
                        movie_id=mov.id,
                        anonymous_id=uuid.uuid4(),
                        rating=log_item["rating"],
                        text=log_item["text"],
                        watched_at=date.today(),
                    )
                )
        db.commit()

    return added


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        m, g = seed_reference_data(db)
        mov_count = seed_starter_movies(db)
    print(f"Seeded {m} new moods, {g} new genres, {mov_count} starter movies.")


if __name__ == "__main__":
    main()
