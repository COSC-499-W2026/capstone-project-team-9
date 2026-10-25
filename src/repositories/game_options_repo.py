"""Read-only access to the Language and Difficulty lookup tables."""
from sqlmodel import Session, select

from models import Difficulty, Language


def get_all_languages(session: Session) -> list[Language]:
    return list(session.exec(select(Language).order_by(Language.name)).all())


def get_all_difficulties(session: Session) -> list[Difficulty]:
    """Ordered by id, so seed data listed easiest-first stays in that order."""
    return list(session.exec(select(Difficulty).order_by(Difficulty.id)).all())


def get_language(session: Session, language_id: int) -> Language | None:
    return session.get(Language, language_id)


def get_difficulty(session: Session, difficulty_id: int) -> Difficulty | None:
    return session.get(Difficulty, difficulty_id)