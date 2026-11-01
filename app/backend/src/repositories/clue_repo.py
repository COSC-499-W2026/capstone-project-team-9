"""Read access to the Clue table."""
from sqlmodel import Session, func, select

from models import Clue

class ClueRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_random_clue_ids(self, language_id: int, difficulty_id: int, count: int) -> list[int]:
        """
        Up to `count` random clue ids for the language and difficulty (never loads audio).
        """
        statement = (
            select(Clue.id)
            .where(Clue.language_id == language_id, Clue.difficulty_id == difficulty_id)
            .order_by(func.random())
            .limit(count)
        )
        return list(self.session.exec(statement).all())

    def count_clues(self, language_id: int, difficulty_id: int) -> int:
        """How many clues exist for the language and difficulty."""
        statement = select(func.count(Clue.id)).where(
            Clue.language_id == language_id, Clue.difficulty_id == difficulty_id
        )
        return self.session.exec(statement).one()