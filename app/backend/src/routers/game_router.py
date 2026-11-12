from fastapi import APIRouter, HTTPException, status

from schemas.game_schema import GameCreate, GameResponse
from core.dependencies import GameServiceDep

router = APIRouter(prefix="/games", tags=["games"])


@router.post("", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
def create_custom_game(body: GameCreate, game_service: GameServiceDep):
    """Create a custom game and return its ruleset."""
    try:
        game = game_service.create_game(body)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    return GameResponse.model_validate(game)