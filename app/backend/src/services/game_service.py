"""Process "Start custom game": validate the settings, pick random clues, save the game."""
from dataclasses import dataclass

from sqlmodel import Session

from models import Game
from repositories.clue_repo import get_random_clue_ids
from repositories.game_options_repo import get_difficulty, get_language
from repositories.game_repo import add_game
from schemas.game_schema import GameCreate
from services.game_options_service import MAX_GAME_LENGTH, MIN_GAME_LENGTH


@dataclass(frozen=True)
class StartedGame:
    game: Game
    clue_ids: list[int]


def _validate_settings(session: Session, settings: GameCreate) -> None:
    """Raise ValueError if any chosen setting is not an available option."""
    if not MIN_GAME_LENGTH <= settings.num_clues <= MAX_GAME_LENGTH:
        raise ValueError(
            f"Game length must be between {MIN_GAME_LENGTH} and {MAX_GAME_LENGTH}"
        )
    if get_language(session, settings.language_id) is None:
        raise ValueError("Language does not exist")
    if get_difficulty(session, settings.difficulty_id) is None:
        raise ValueError("Difficulty does not exist")


def start_game(
    session: Session, settings: GameCreate, creator_id: int | None = None
) -> StartedGame:
    """
    Create a custom game and pick its clues.
    The game is only saved if enough clues exist, so a failed start leaves no orphan game.
    creator_id stays None until login exists.
    """
    _validate_settings(session, settings)
    clue_ids = get_random_clue_ids(
        session, settings.language_id, settings.difficulty_id, settings.num_clues
    )
    if len(clue_ids) < settings.num_clues:
        raise ValueError("Not enough clues available for these settings")
    game = add_game(session, Game(
        num_clues=settings.num_clues,
        language_id=settings.language_id,
        difficulty_id=settings.difficulty_id,
        creator_id=creator_id,
    ))
    return StartedGame(game, clue_ids)