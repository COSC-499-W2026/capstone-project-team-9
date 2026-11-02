"""Process "Start play": pick random clues for a game and save the play."""
from dataclasses import dataclass

from sqlmodel import Session

from models import Play
from repositories.clue_repo import get_random_clue_ids
from repositories.game_repo import get_game
from repositories.play_repo import add_play_with_clues


class GameNotFoundError(Exception):
    """Raised when a play is started for a game that does not exist."""


@dataclass(frozen=True)
class StartedPlay:
    play: Play
    clue_ids: list[int]


def start_play(session: Session, game_id: int, user_id: int | None = None) -> StartedPlay:
    """
    Start a play of a game: pick random clues matching the game's ruleset and save them in order.
    Nothing is saved if the game is missing or too few clues exist.
    user_id stays None until login exists.
    """
    game = get_game(session, game_id)
    if game is None:
        raise GameNotFoundError("Game does not exist")
    clue_ids = get_random_clue_ids(
        session, game.language_id, game.difficulty_id, game.num_clues
    )
    if len(clue_ids) < game.num_clues:
        raise ValueError("Not enough clues available for this game")
    play = add_play_with_clues(session, Play(game_id=game.id, user_id=user_id), clue_ids)
    return StartedPlay(play, clue_ids)