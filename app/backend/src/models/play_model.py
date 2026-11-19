from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from core.clock import utc_now


class Play(SQLModel, table=True):
    """One user's attempt at a game."""
    id: int | None = Field(default=None, primary_key=True)
    score: float | None = 0.0
    started_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))
    completed_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    game_id: int | None = Field(default=None, foreign_key="game.id", ondelete="SET NULL")