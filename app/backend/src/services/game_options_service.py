"""Process "Get game options": what a player can pick when creating a game."""
from dataclasses import dataclass

from sqlmodel import Session

from models import Difficulty, Language
from repositories.game_options_repo import get_all_difficulties, get_all_languages

# TODO: confirm the max with the client
MIN_GAME_LENGTH = 1
MAX_GAME_LENGTH = 10


@dataclass(frozen=True)
class GameLengthRange:
    min: int
    max: int


def list_languages(session: Session) -> list[Language]:
    return get_all_languages(session)


def list_difficulties(session: Session) -> list[Difficulty]:
    return get_all_difficulties(session)


def get_game_length_range() -> GameLengthRange:
    return GameLengthRange(MIN_GAME_LENGTH, MAX_GAME_LENGTH)