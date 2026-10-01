from sqlalchemy import Column, ForeignKey, Table

from app.database import Base

# MovieGenre / MovieMood: pure link tables (no extra columns needed in MVP).
movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True, index=True),
)

movie_moods = Table(
    "movie_moods",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("mood_id", ForeignKey("moods.id", ondelete="CASCADE"), primary_key=True, index=True),
)
