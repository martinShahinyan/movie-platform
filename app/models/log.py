from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.movie import Movie

MAX_LOG_LENGTH = 2000


class Log(Base):
    __tablename__ = "logs"
    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 10", name="ck_log_rating_range"),
        # "Recent logs" per movie and globally
        Index("ix_logs_movie_created", "movie_id", "created_at"),
        Index("ix_logs_created", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), index=True)
    anonymous_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    rating: Mapped[int | None]
    text: Mapped[str] = mapped_column(String(MAX_LOG_LENGTH))
    watched_at: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    movie: Mapped[Movie] = relationship(back_populates="logs")
