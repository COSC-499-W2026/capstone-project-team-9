"""Persistence for the Play and PlayClue tables."""

from sqlmodel import Session, select

from models import Play, PlayClue


def add_play_with_clues(session: Session, play: Play, clue_ids: list[int]) -> Play:
    """
    Save a new play and its clue list in one commit. Positions follow the order of clue_ids,
    starting at 1. All clues start unsolved.
    """
    session.add(play)
    session.flush()  # assigns play.id
    session.add_all(
        PlayClue(play_id=play.id, clue_id=clue_id, position=position)
        for position, clue_id in enumerate(clue_ids, start=1)
    )
    session.commit()
    session.refresh(play)
    return play

def get_play(session: Session, play_id: int) -> Play | None:
    return session.get(Play, play_id)


def get_play_clues(session: Session, play_id: int) -> list[PlayClue]:
    """All clues in a play, ordered by position."""
    statement = select(PlayClue).where(PlayClue.play_id == play_id).order_by(PlayClue.position)
    return list(session.exec(statement).all())