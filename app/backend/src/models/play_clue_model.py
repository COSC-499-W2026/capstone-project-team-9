from datetime import datetime

from sqlalchemy import DateTime, UniqueConstraint
from sqlmodel import Field, SQLModel


class PlayClue(SQLModel, table=True):
    """
    A clue in one play: the full plan (position) plus progress (solved_at, attempts).
    Rows are created all at once when the play starts.
    """
    __table_args__ = (UniqueConstraint("play_id", "position"),)

    play_id: int = Field(foreign_key="play.id", primary_key=True, ondelete="CASCADE")
    clue_id: int = Field(foreign_key="clue.id", primary_key=True)
    position: int
    solved_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    attempts: int = 0