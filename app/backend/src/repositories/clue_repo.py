"""Read access to the Clue table."""
from sqlmodel import Session, func, select

from models import Clue, Target


def get_random_clue_ids(
    session: Session, language_id: int, difficulty_id: int, count: int
) -> list[int]:
    """Up to `count` random clue ids for the language and difficulty (never loads audio)."""
    statement = (
        select(Clue.id)
        .where(Clue.language_id == language_id, Clue.difficulty_id == difficulty_id)
        .order_by(func.random())
        .limit(count)
    )
    return list(session.exec(statement).all())

def count_clues(session: Session, language_id: int, difficulty_id: int) -> int:
    """How many clues exist for the language and difficulty."""
    statement = select(func.count(Clue.id)).where(
        Clue.language_id == language_id, Clue.difficulty_id == difficulty_id
    )
    return session.exec(statement).one()

def get_target_by_id(session: Session, clue_id: int) -> Target | None:
    """Get a target by clue id (never loads audio)."""
    statement = select(Target).join(Clue, Clue.target_id == Target.id).where(Clue.id == clue_id)
    return session.exec(statement).first()