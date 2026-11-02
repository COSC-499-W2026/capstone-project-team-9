from sqlmodel import Session, select

from models import Clue, Target


def get_target_by_id(session: Session, clue_id: int) -> Target | None:
    """Get a target by clue id (never loads audio)."""
    statement = select(Target).join(Clue, Clue.target_id == Target.id).where(Clue.id == clue_id)
    return session.exec(statement).first()