from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from core.db import get_session
from schemas.game_schema import ClueResponse, GameCreate, GameResponse, GameStartResponse
from services.game_service import start_game

router = APIRouter(prefix="/games", tags=["games"])


@router.post("", response_model=GameStartResponse, status_code=status.HTTP_201_CREATED)
def start_custom_game(body: GameCreate, session: Session = Depends(get_session)):
    """Create a custom game and return its settings plus a randomized list of clues."""
    try:
        started = start_game(session, body)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return GameStartResponse(
        game=GameResponse.model_validate(started.game),
        clues=[ClueResponse(id=clue_id) for clue_id in started.clue_ids],
    )