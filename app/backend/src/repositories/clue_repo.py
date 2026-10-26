"""Read access to the Clue table."""
from sqlmodel import Session, func, select

from models import Clue


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