from datetime import datetime
from enum import Enum

from sqlalchemy import CheckConstraint, Column, DateTime, Text, text
from sqlmodel import Field, SQLModel

from core.clock import utc_now


class UserRole(str, Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class User(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint(
            '"role" IN (\'student\', \'instructor\', \'admin\')',
            name="ck_user_role",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(max_length=320, unique=True, index=True)
    hashed_password: str = Field(
        sa_column=Column("password", Text, nullable=False),
    )
    role: str = Field(
        default=UserRole.STUDENT.value,
        sa_column=Column(
            Text,
            nullable=False,
            server_default=text("'student'"),
        ),
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
    )