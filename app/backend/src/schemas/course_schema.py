from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CourseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, pattern=r"\S")  # pattern rejects all-whitespace names
    language_id: int


class EnrollRequest(BaseModel):
    access_code: str = Field(min_length=6, max_length=6)

    @field_validator("access_code", mode="before")
    @classmethod
    def normalize_access_code(cls, value):
        """Accept codes typed with surrounding spaces or in lowercase."""
        return value.strip().upper() if isinstance(value, str) else value


class AccessCodeResponse(BaseModel):
    access_code: str


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
