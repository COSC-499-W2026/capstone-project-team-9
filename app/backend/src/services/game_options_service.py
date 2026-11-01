from dataclasses import dataclass

from sqlmodel import Session

from models import Difficulty, Language
from repositories.game_options_repo import get_all_difficulties, get_all_languages
from repositories.clue_repo import count_clues

# TODO: confirm the max with the client
MIN_GAME_LENGTH = 1
MAX_GAME_LENGTH = 10


@dataclass(frozen=True)
class GameLengthRange:
    min: int
    max: int

class GameOptionsService:
    """
    Service for processing "Get game options": what a player can pick when creating a game.
    """
    def __init__(self, session: Session, clue_repo: ClueRepository):
        self.session = session
        self.clue_repo = clue_repo

def list_languages(session: Session) -> list[Language]:
    return get_all_languages(session)


def list_difficulties(session: Session) -> list[Difficulty]:
    return get_all_difficulties(session)


def get_game_length_range(
    session: Session, language_id: int, difficulty_id: int
) -> GameLengthRange:
    """Playable game lengths for this combo. (0, 0) means no game can be made."""
    available = count_clues(session, language_id, difficulty_id)
    if available == 0:
        return GameLengthRange(0, 0)
    return GameLengthRange(MIN_GAME_LENGTH, min(MAX_GAME_LENGTH, available))