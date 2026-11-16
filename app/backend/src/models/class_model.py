from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from core.clock import utc_now

class Class(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    language: str | None = None
    owner_id: int | None = Field(default=None, foreign_key="user.id", ondelete="SET NULL")
    access_code: str | None = Field(default=None, unique=True)
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))