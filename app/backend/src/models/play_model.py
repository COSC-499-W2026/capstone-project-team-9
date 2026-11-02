from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from core.clock import utc_now


class Play(SQLModel, table=True):
    """One user's attempt at a game."""
    id: int | None = Field(default=None, primary_key=True)
    score: float | None = None
    started_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))
    # Nullable until login exists, like creator_id on Game; then make it required
    user_id: int | None = Field(default=None, foreign_key="user.id", ondelete="CASCADE")
    game_id: int | None = Field(default=None, foreign_key="game.id", ondelete="SET NULL")