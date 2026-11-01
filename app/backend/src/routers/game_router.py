from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from core.db import get_session
from schemas.game_schema import GameCreate, GameResponse
from services.game_service import create_game

router = APIRouter(prefix="/games", tags=["games"])


@router.post("", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
def create_custom_game(body: GameCreate, session: Session = Depends(get_session)):
    """Create a custom game and return its ruleset."""
    try:
        game = create_game(session, body)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return GameResponse.model_validate(game)