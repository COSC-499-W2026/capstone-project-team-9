from typing import Annotated
from fastapi import Depends
from sqlmodel import Session
from core.db import get_session
from repositories import ClueRepository, GameRepository, GameOptionsRepository
from services import GameOptionsService, GameService, PlayService

# SESSION DEPENDENCIES -----------------------------------------------------------

SessionDep = Annotated[Session, Depends(get_session)]

# REPOSITORY DEPENDENCIES --------------------------------------------------------

def get_clue_repository(session: SessionDep) -> ClueRepository:
    return ClueRepository(session)

def get_game_options_repository(session: SessionDep) -> GameOptionsRepository:
    return GameOptionsRepository(session)

def get_game_repository(session: SessionDep) -> GameRepository:
    return GameRepository(session)

ClueRepositoryDep = Annotated[ClueRepository, Depends(get_clue_repository)]
GameOptionsRepositoryDep = Annotated[GameOptionsRepository, Depends(get_game_options_repository)]
GameRepositoryDep = Annotated[GameRepository, Depends(get_game_repository)]

# SERVICE DEPENDENCIES --------------------------------------------------------

def get_game_options_service(
    game_options_repo: GameOptionsRepositoryDep,
    clue_repo: ClueRepositoryDep
) -> GameOptionsService:
    return GameOptionsService(game_options_repo, clue_repo)

def get_game_service(
    game_repo: GameRepositoryDep,
    game_options_repo: GameOptionsRepositoryDep,
    clue_repo: ClueRepositoryDep
) -> GameService:
    return GameService(game_repo, game_options_repo, clue_repo)

def get_play_service(
    session: SessionDep,
    clue_repo: ClueRepositoryDep
) -> PlayService:
    return PlayService(session, clue_repo)

GameOptionsServiceDep = Annotated[GameOptionsService, Depends(get_game_options_service)]
GameServiceDep = Annotated[GameService, Depends(get_game_service)]
PlayServiceDep = Annotated[PlayService, Depends(get_play_service)]