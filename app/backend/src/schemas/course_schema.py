from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CourseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, pattern=r"\S")  # pattern rejects all-whitespace names
    language_id: int


class CourseResponse(BaseModel):
    """access_code is only included for users with instructor permissions in the course."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    language_id: int
    owner_id: int | None
    is_instructor: bool
    access_code: str | None = None
    created_at: datetime
