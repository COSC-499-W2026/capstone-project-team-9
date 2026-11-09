from sqlmodel import select

from models import Clue, Target
from repositories import BaseRepository


class TargetRepository(BaseRepository):
    """
    Repository class for interacting with target data.
    """

    def get_target_for_clue(self, clue_id: int) -> Target | None:
        """Give `clue_id`, get that clue's target"""
        statement = select(Target).join(Clue, Clue.target_id == Target.id).where(Clue.id == clue_id)
        return self.session.exec(statement).first()