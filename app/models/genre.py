from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.associations import movie_genres

if TYPE_CHECKING:
    from app.models.movie import Movie


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    movies: Mapped[list[Movie]] = relationship(
        secondary=movie_genres, back_populates="genres", lazy="noload"
    )
