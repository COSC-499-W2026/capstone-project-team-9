from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from core.clock import utc_now


class Clue(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    audio: bytes
    difficulty_id: int = Field(foreign_key="difficulty.id")
    language_id: int = Field(foreign_key="language.id")
    target_id: int = Field(foreign_key="target.id")
    creator_id: int | None = None  # becomes a foreign key once the User model exists
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))
    updated_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))