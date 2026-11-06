"""Persistence for the Play and PlayClue tables."""

from sqlmodel import Session, select, func

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


def count_play_clues(session: Session, play_id: int) -> int:
    """How many clues the play has in total."""
    statement = select(func.count()).select_from(PlayClue).where(PlayClue.play_id == play_id)
    return session.exec(statement).one()


def count_solved_play_clues(session: Session, play_id: int) -> int:
    """How many of the play's clues are solved."""
    statement = select(func.count()).select_from(PlayClue).where(
        PlayClue.play_id == play_id, PlayClue.solved_at.is_not(None)
    )
    return session.exec(statement).one()


def get_current_clue_id(session: Session, play_id: int) -> int | None:
    """The lowest-position clue in the play that isn't solved yet, or None if all are solved."""
    statement = (
        select(PlayClue.clue_id)
        .where(PlayClue.play_id == play_id, PlayClue.solved_at.is_(None))
        .order_by(PlayClue.position)
        .limit(1)
    )
    return session.exec(statement).first()