from sqlmodel import select

from models import Clue, Target
from repositories import BaseRepository


class TargetRepository(BaseRepository):
    """
    Repository class for interacting with target data.
    """

    def get_target_by_id(self, clue_id: int) -> Target | None:
        """Get a target by clue id (never loads audio)."""
        statement = select(Target).join(Clue, Clue.target_id == Target.id).where(Clue.id == clue_id)
        return self.session.exec(statement).first()