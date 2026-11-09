"""Process "Start play": pick random clues for a game and save the play."""
from dataclasses import dataclass

from models import Play
from repositories import ClueRepository, GameRepository, PlayRepository
from services import AnswerService

 
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
    def __init__(
        self,
        answer_service: AnswerService,
        play_repo: PlayRepository,
        game_repo: GameRepository,
        clue_repo: ClueRepository
    ):
        self.answer_service = answer_service
        self.play_repo = play_repo
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
        play = self.play_repo.add_play_with_clues(Play(game_id=game.id, user_id=user_id), clue_ids)
        return StartedPlay(play, clue_ids)

    def get_play_state(self, play_id: int) -> PlayState:
        """A play's progress. Raises PlayNotFoundError if the play is missing."""
        play = self.play_repo.get_play(play_id)
        if play is None:
            raise PlayNotFoundError("Play does not exist")
        return PlayState(
            play=play,
            current_clue_id=self.play_repo.get_current_clue_id(play_id),
            total_clues=self.play_repo.count_play_clues(play_id),
            solved_clues=self.play_repo.count_solved_play_clues(play_id),
        )

    def submit_answer(
        self, play_id: int, clue_id: int, image_bytes: bytes, lat: float, lon: float
    ) -> PlayAnswerResult:
        """
        Check a player's photo and location against a clue in their play, and record the attempt.
        A correct answer solves the clue, and solving the last clue completes the play.
        An unreadable image raises ValueError before anything is recorded.
        """
        play = self.play_repo.get_play(play_id)
        if play is None:
            raise PlayNotFoundError("Play does not exist")
        play_clue = self.play_repo.get_play_clue(play_id, clue_id)
        if play_clue is None:
            raise ClueNotInPlayError("Clue is not part of this play")
        if play_clue.solved_at is not None:
            raise ClueAlreadySolvedError("Clue is already solved")
        if self.play_repo.get_current_clue_id(play_id) != clue_id:
            raise ClueNotCurrentError("Clue is not the current clue")

        answer = self.answer_service.verify_answer(clue_id, image_bytes, lat, lon)
        self.play_repo.record_attempt(play_clue, answer.correct)

        play_complete = answer.correct and self.play_repo.get_current_clue_id(play_id) is None
        if play_complete:
            self.play_repo.mark_play_complete(play)
        return PlayAnswerResult(answer.correct, answer.message, play_clue.attempts, play_complete)
