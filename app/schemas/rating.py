from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RatingCreate(BaseModel):
    value: int = Field(..., ge=1, le=10, description="Rating value from 1 to 10")


class RatingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    movie_id: int
    anonymous_id: uuid.UUID
    value: int
    created_at: datetime
    updated_at: datetime


class MovieRatingStatsOut(BaseModel):
    user_rating: int | None = None
    community_rating: float
    vote_count: int
