"""Process "Start play": pick random clues for a game and save the play."""
from dataclasses import dataclass

from sqlmodel import Session

from models import Play
from repositories import ClueRepository, GameRepository
from repositories.play_repo import (
    add_play_with_clues, get_play, count_play_clues,
    count_solved_play_clues, get_current_clue_id,
    get_play_clue, record_attempt, mark_play_complete
)
from services.answer_service import verify_answer

 
class GameNotFoundError(Exception):
    """Raised when a play is started for a game that does not exist."""

class PlayNotFoundError(Exception):
    """Raised when a play id does not exist."""

class ClueNotInPlayError(Exception):
    """Raised when an answer is submitted for a clue that isn't part of the play."""


class ClueAlreadySolvedError(Exception):
    """Raised when an answer is submitted for a clue that is already solved."""

class ClueNotCurrentError(Exception):
    """Raised when an answer is submitted for a clue that isn't the play's current clue."""

@dataclass(frozen=True)
class PlayState:
    play: Play
    current_clue_id: int | None  # lowest-position unsolved clue, None when all are solved
    total_clues: int
    solved_clues: int


@dataclass(frozen=True)
class StartedPlay:
    play: Play
    clue_ids: list[int]

@dataclass(frozen=True)
class PlayAnswerResult:
    correct: bool
    message: str
    attempts: int  # attempts on this clue so far, including this one
    play_complete: bool

class PlayService:
    def __init__(self, session: Session, game_repo: GameRepository, clue_repo: ClueRepository):
        self.session = session
        self.game_repo = game_repo
        self.clue_repo = clue_repo

    def start_play(self, game_id: int, user_id: int | None = None) -> StartedPlay:
        """
        Start a play of a game: pick random clues matching the game's ruleset and save them in order.
        Nothing is saved if the game is missing or too few clues exist.
        user_id stays None until login exists.
        """
        game = self.game_repo.get_game(game_id)
        if game is None:
            raise GameNotFoundError("Game does not exist")
        clue_ids = self.clue_repo.get_random_clue_ids(
            game.language_id, game.difficulty_id, game.num_clues
        )
        if len(clue_ids) < game.num_clues:
            raise ValueError("Not enough clues available for this game")
        play = add_play_with_clues(self.session, Play(game_id=game.id, user_id=user_id), clue_ids)
        return StartedPlay(play, clue_ids)

    def get_play_state(self, play_id: int) -> PlayState:
        """A play's progress. Raises PlayNotFoundError if the play is missing."""
        play = get_play(self.session, play_id)
        if play is None:
            raise PlayNotFoundError("Play does not exist")
        return PlayState(
            play=play,
            current_clue_id=get_current_clue_id(self.session, play_id),
            total_clues=count_play_clues(self.session, play_id),
            solved_clues=count_solved_play_clues(self.session, play_id),
        )

    def submit_answer(
        self, play_id: int, clue_id: int, image_bytes: bytes, lat: float, lon: float
    ) -> PlayAnswerResult:
        """
        Check a player's photo and location against a clue in their play, and record the attempt.
        A correct answer solves the clue, and solving the last clue completes the play.
        An unreadable image raises ValueError before anything is recorded.
        """
        play = get_play(self.session, play_id)
        if play is None:
            raise PlayNotFoundError("Play does not exist")
        play_clue = get_play_clue(self.session, play_id, clue_id)
        if play_clue is None:
            raise ClueNotInPlayError("Clue is not part of this play")
        if play_clue.solved_at is not None:
            raise ClueAlreadySolvedError("Clue is already solved")
        if get_current_clue_id(self.session, play_id) != clue_id:
            raise ClueNotCurrentError("Clue is not the current clue")

        answer = verify_answer(self.session, clue_id, image_bytes, lat, lon)
        record_attempt(self.session, play_clue, answer.correct)

        play_complete = answer.correct and get_current_clue_id(self.session, play_id) is None
        if play_complete:
            mark_play_complete(self.session, play)
        return PlayAnswerResult(answer.correct, answer.message, play_clue.attempts, play_complete)
    