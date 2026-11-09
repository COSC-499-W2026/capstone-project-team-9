"""
Development-only helpers for testing the game by hand.

Only registered when ENV=development (see main.py), so these never exist in production.
"""
from fastapi import APIRouter, HTTPException, status

from core.dependencies import SessionDep
from repositories.target_repo import get_target_for_clue

router = APIRouter(prefix="/dev", tags=["dev"])


@router.get("/clues/{clue_id}/room")
def get_clue_room(clue_id: int, session: SessionDep) -> dict[str, str]:
    """The room a clue points to, so testers know which sign to photograph."""
    target = get_target_for_clue(session, clue_id)
    if target is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Clue does not exist")
    return {"room": target.name}
