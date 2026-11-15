from fastapi import APIRouter, HTTPException, status

from schemas.game_schema import GameCreate, GameResponse
from core.dependencies import CurrentUserDep, GameServiceDep

router = APIRouter(prefix="/games", tags=["games"])


@router.post("", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
def create_custom_game(body: GameCreate, game_service: GameServiceDep, current_user: CurrentUserDep):
    """Create a custom game owned by the logged-in user and return its ruleset."""
    try:
        game = game_service.create_game(body, current_user.id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return GameResponse.model_validate(game)