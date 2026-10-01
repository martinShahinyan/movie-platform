from __future__ import annotations

import uuid
from datetime import date
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Log, Movie


def create_log(
    db: Session,
    movie_id: int,
    anonymous_id: uuid.UUID,
    text: str,
    rating: int | None = None,
    watched_at: date | None = None,
) -> Log:
    if watched_at is None:
        watched_at = date.today()

    log_entry = Log(
        movie_id=movie_id,
        anonymous_id=anonymous_id,
        rating=rating,
        text=text.strip(),
        watched_at=watched_at,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


def get_movie_logs(db: Session, movie_id: int, limit: int = 20) -> Sequence[Log]:
    stmt = (
        select(Log)
        .where(Log.movie_id == movie_id)
        .order_by(Log.created_at.desc())
        .limit(limit)
    )
    return db.scalars(stmt).all()


def get_recent_logs(db: Session, limit: int = 10) -> Sequence[Log]:
    stmt = (
        select(Log)
        .options(joinedload(Log.movie))
        .order_by(Log.created_at.desc())
        .limit(limit)
    )
    return db.scalars(stmt).all()


def delete_log(db: Session, log_id: int) -> bool:
    log_entry = db.get(Log, log_id)
    if not log_entry:
        return False
    db.delete(log_entry)
    db.commit()
    return True
