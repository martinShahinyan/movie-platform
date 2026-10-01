from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class LogCreate(BaseModel):
    rating: int | None = Field(None, ge=1, le=10, description="Optional rating 1-10")
    text: str = Field(..., min_length=1, max_length=2000, description="Log commentary")
    watched_at: date | None = None


class LogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    movie_id: int
    anonymous_id: uuid.UUID
    rating: int | None
    text: str
    watched_at: date
    created_at: datetime
    movie_title: str | None = None
    movie_slug: str | None = None
    poster_path: str | None = None
