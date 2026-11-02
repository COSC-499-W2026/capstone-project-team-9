from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from core.db import get_session
from schemas.play_schema import ClueResponse, PlayResponse, PlayStartResponse
from services.play_service import GameNotFoundError, start_play

router = APIRouter(tags=["plays"])


@router.post(
    "/games/{game_id}/plays",
    response_model=PlayStartResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_game_play(game_id: int, session: Session = Depends(get_session)):
    """Start a play of a game and return the play plus its ordered list of clue ids."""
    try:
        started = start_play(session, game_id)
    except GameNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return PlayStartResponse(
        play=PlayResponse.model_validate(started.play),
        clues=[ClueResponse(id=clue_id) for clue_id in started.clue_ids],
    )