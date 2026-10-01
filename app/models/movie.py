from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.associations import movie_genres, movie_moods

if TYPE_CHECKING:
    from app.models.genre import Genre
    from app.models.log import Log
    from app.models.mood import Mood
    from app.models.rating import Rating


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True)
    tmdb_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    original_title: Mapped[str | None] = mapped_column(String(255))
    overview: Mapped[str | None] = mapped_column(Text)
    poster_path: Mapped[str | None] = mapped_column(String(255))
    backdrop_path: Mapped[str | None] = mapped_column(String(255))
    release_date: Mapped[date | None] = mapped_column(Date, index=True)
    runtime: Mapped[int | None] = mapped_column(Integer)
    vote_average: Mapped[float] = mapped_column(Float, default=0.0, server_default="0", index=True)
    vote_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    original_language: Mapped[str | None] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # selectin avoids N+1 when rendering lists of movie cards
    genres: Mapped[list[Genre]] = relationship(
        secondary=movie_genres, back_populates="movies", lazy="selectin"
    )
    moods: Mapped[list[Mood]] = relationship(
        secondary=movie_moods, back_populates="movies", lazy="selectin"
    )
    ratings: Mapped[list[Rating]] = relationship(
        back_populates="movie", cascade="all, delete-orphan", lazy="noload"
    )
    logs: Mapped[list[Log]] = relationship(
        back_populates="movie", cascade="all, delete-orphan", lazy="noload"
    )

    @property
    def year(self) -> int | None:
        return self.release_date.year if self.release_date else None
