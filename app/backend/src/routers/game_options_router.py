from fastapi import APIRouter, Depends
from sqlmodel import Session

from schemas.game_options_schema import DifficultyResponse, LanguageResponse, GameLengthResponse
from core.dependencies import GameOptionsServiceDep

router = APIRouter(tags=["game options"])


@router.get("/languages", response_model=list[LanguageResponse])
def get_languages(game_options_service: GameOptionsServiceDep):
    """All languages a game can be created in."""
    return game_options_service.list_languages()


@router.get("/difficulties", response_model=list[DifficultyResponse])
def get_difficulties(game_options_service: GameOptionsServiceDep):
    """All difficulties a game can be created with."""
    return game_options_service.list_difficulties()


@router.get("/game-lengths", response_model=GameLengthResponse)
def get_game_lengths(
    language_id: int,
    difficulty_id: int,
    game_options_service: GameOptionsServiceDep,
):
    """Smallest and largest number of clues a game can have for this language and difficulty."""
    return game_options_service.get_game_length_range(language_id, difficulty_id)