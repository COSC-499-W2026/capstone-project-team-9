from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from core.clock import utc_now


class Game(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    num_clues: int
    language_id: int = Field(foreign_key="language.id")
    difficulty_id: int = Field(foreign_key="difficulty.id")
    due_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    # Plain ints until the User and Course models exist; then add foreign_key="user.id" / "course.id"
    course_id: int | None = None
    creator_id: int | None = None
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))
    updated_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))