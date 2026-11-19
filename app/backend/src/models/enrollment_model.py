from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from core.clock import utc_now

class Enrollment(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True, ondelete="CASCADE")
    course_id: int = Field(foreign_key="course.id", primary_key=True, ondelete="CASCADE", index=True)
    is_instructor: bool = False
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))