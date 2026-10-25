from fastapi import APIRouter, Depends
from sqlmodel import Session

from core.db import get_session
from schemas.game_options_schema import DifficultyResponse, LanguageResponse, GameLengthResponse
from services.game_options_service import list_difficulties, list_languages, get_game_length_range

router = APIRouter(tags=["game options"])


@router.get("/languages", response_model=list[LanguageResponse])
def get_languages(session: Session = Depends(get_session)):
    """All languages a game can be created in."""
    return list_languages(session)


@router.get("/difficulties", response_model=list[DifficultyResponse])
def get_difficulties(session: Session = Depends(get_session)):
    """All difficulties a game can be created with."""
    return list_difficulties(session)


@router.get("/game-lengths", response_model=GameLengthResponse)
def get_game_lengths():
    """Smallest and largest number of clues a game can have (for the length slider)."""
    return get_game_length_range()