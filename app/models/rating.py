from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.movie import Movie


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (
        # one rating per anonymous visitor per movie; they may update it
        UniqueConstraint("movie_id", "anonymous_id", name="uq_rating_movie_anon"),
        CheckConstraint("value BETWEEN 1 AND 10", name="ck_rating_value_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), index=True)
    anonymous_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    value: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    movie: Mapped[Movie] = relationship(back_populates="ratings")
