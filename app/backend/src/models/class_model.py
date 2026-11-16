from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from core.clock import utc_now

class Class(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=100)
    language_id: int | None = Field(default=None, foreign_key="language.id")
    owner_id: int | None = Field(default=None, foreign_key="user.id", ondelete="SET NULL", index=True)
    access_code: str | None = Field(default=None, unique=True)
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))