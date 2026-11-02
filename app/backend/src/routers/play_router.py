from fastapi import APIRouter,  HTTPException, status
from sqlmodel import Session

from schemas.play_schema import ClueResponse, PlayResponse, PlayStartResponse
from services.play_service import GameNotFoundError
from core.dependencies import PlayServiceDep

router = APIRouter(tags=["plays"])


@router.post(
    "/games/{game_id}/plays",
    response_model=PlayStartResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_game_play(game_id: int, play_service: PlayServiceDep):
    """Start a play of a game and return the play plus its ordered list of clue ids."""
    try:
        started = play_service.start_play(game_id)
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