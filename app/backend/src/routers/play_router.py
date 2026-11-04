from fastapi import APIRouter,  HTTPException, status
from sqlmodel import Session

from schemas.play_schema import ClueResponse, PlayResponse, PlayStartResponse, PlayStateResponse
from services.play_service import GameNotFoundError, PlayNotFoundError
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
@router.get("/plays/{play_id}", response_model=PlayStateResponse)
def get_play_state(play_id: int, play_service: PlayServiceDep):
    """Progress of a play: its clues in order and which one is next."""
    try:
        state = play_service.get_play_state(play_id)
    except PlayNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return PlayStateResponse(
        id=state.play.id,
        game_id=state.play.game_id,
        completed=state.play.completed_at is not None,
        current_clue_id=state.current_clue_id,
        total_clues=state.total_clues,
        solved_clues=state.solved_clues,
    )