"""Persistence for the Play and PlayClue tables."""

from sqlmodel import select, func

from repositories import BaseRepository
from models import Play, PlayClue

from core.clock import utc_now

class PlayRepository(BaseRepository):
    """
    Repository class for interacting with Play data
    """

    def add_play_with_clues(self, play: Play, clue_ids: list[int]) -> Play:
        """
        Save a new play and its clue list in one commit. Positions follow the order of clue_ids,
        starting at 1. All clues start unsolved.
        """
        self.session.add(play)
        self.session.flush()  # assigns play.id
        self.session.add_all(
            PlayClue(play_id=play.id, clue_id=clue_id, position=position)
            for position, clue_id in enumerate(clue_ids, start=1)
        )
        self.session.commit()
        self.session.refresh(play)
        return play

    def get_play(self, play_id: int) -> Play | None:
        return self.session.get(Play, play_id)


    def count_play_clues(self, play_id: int) -> int:
        """How many clues the play has in total."""
        statement = select(func.count()).select_from(PlayClue).where(PlayClue.play_id == play_id)
        return self.session.exec(statement).one()


    def count_solved_play_clues(self, play_id: int) -> int:
        """How many of the play's clues are solved."""
        statement = select(func.count()).select_from(PlayClue).where(
            PlayClue.play_id == play_id, PlayClue.solved_at.is_not(None)
        )
        return self.session.exec(statement).one()


    def get_current_clue_id(self, play_id: int) -> int | None:
        """The lowest-position clue in the play that isn't solved yet, or None if all are solved."""
        statement = (
            select(PlayClue.clue_id)
            .where(PlayClue.play_id == play_id, PlayClue.solved_at.is_(None))
            .order_by(PlayClue.position)
            .limit(1)
        )
        return self.session.exec(statement).first()

    def get_play_clue(self, play_id: int, clue_id: int) -> PlayClue | None:
        return self.session.get(PlayClue, (play_id, clue_id))


    def record_attempt(self, play_clue: PlayClue, solved: bool) -> PlayClue:
        """Count one more attempt on a clue, and mark it solved if the attempt was correct."""
        play_clue.attempts += 1
        if solved:
            play_clue.solved_at = utc_now()
        self.session.add(play_clue)
        self.session.commit()
        self.session.refresh(play_clue)
        return play_clue


    def mark_play_complete(self, play: Play) -> Play:
        play.completed_at = utc_now()
        self.session.add(play)
        self.session.commit()
        self.session.refresh(play)
        return play