"""Process "Start play": pick random clues for a game and save the play."""
from dataclasses import dataclass

from sqlmodel import Session

from models import Play
from repositories import ClueRepository, GameRepository
from repositories.play_repo import add_play_with_clues, get_play, count_play_clues, count_solved_play_clues, get_current_clue_id

 
class GameNotFoundError(Exception):
    """Raised when a play is started for a game that does not exist."""

class PlayNotFoundError(Exception):
    """Raised when a play id does not exist."""

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
    