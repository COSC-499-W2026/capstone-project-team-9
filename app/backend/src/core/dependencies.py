from typing import Annotated
from fastapi import Depends
from sqlmodel import Session
from core.db import get_session
from repositories import ClueRepository
from services import GameOptionsService

def get_clue_repository(session: Session = Depends(get_session)) -> ClueRepository:
    return ClueRepository(session)

def get_game_options_service(
    session: Session = Depends(get_session),
    clue_repo: ClueRepository = Depends(get_clue_repository)
) -> GameOptionsService:
    return GameOptionsService(session, clue_repo)

GameOptionsServiceDep = Annotated[GameOptionsService, Depends(get_game_options_service)]