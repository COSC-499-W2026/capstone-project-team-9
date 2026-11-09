from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from core.db import get_session
from core.security import decode_access_token
from models import User
from repositories import ClueRepository, GameRepository, GameOptionsRepository, PlayRepository, TargetRepository
from repositories.user_repo import get_by_id
from services import GameOptionsService, GameService, PlayService, LocationService, AnswerService

# SESSION DEPENDENCIES -----------------------------------------------------------

SessionDep = Annotated[Session, Depends(get_session)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
) -> User | None:
    user_id = decode_access_token(token)
    return get_by_id(session, user_id) if user_id is not None else None


CurrentUserDep = Annotated[User | None, Depends(get_current_user)]

# REPOSITORY DEPENDENCIES --------------------------------------------------------

def get_clue_repository(session: SessionDep) -> ClueRepository:
    return ClueRepository(session)

def get_game_options_repository(session: SessionDep) -> GameOptionsRepository:
    return GameOptionsRepository(session)

def get_game_repository(session: SessionDep) -> GameRepository:
    return GameRepository(session)

def get_target_repository(session: SessionDep) -> TargetRepository:
    return TargetRepository(session)

def get_play_repository(session: SessionDep) -> PlayRepository:
    return PlayRepository(session)

ClueRepositoryDep = Annotated[ClueRepository, Depends(get_clue_repository)]
GameOptionsRepositoryDep = Annotated[GameOptionsRepository, Depends(get_game_options_repository)]
GameRepositoryDep = Annotated[GameRepository, Depends(get_game_repository)]
TargetRepositoryDep = Annotated[TargetRepository, Depends(get_target_repository)]
PlayRepositoryDep = Annotated[PlayRepository, Depends(get_play_repository)]

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

def get_location_service() -> LocationService:
    return LocationService()

def get_answer_service(
    location_service: LocationServiceDep,
    target_repo: TargetRepository
) -> AnswerService:
    return AnswerService(location_service, target_repo)

def get_play_service(
    answer_service: AnswerServiceDep,
    play_repo: PlayRepositoryDep,
    game_repo: GameRepositoryDep,
    clue_repo: ClueRepositoryDep
) -> PlayService:
    return PlayService(answer_service, play_repo, game_repo, clue_repo)


GameOptionsServiceDep = Annotated[GameOptionsService, Depends(get_game_options_service)]
GameServiceDep = Annotated[GameService, Depends(get_game_service)]
LocationServiceDep = Annotated[LocationService, Depends(get_location_service)]
AnswerServiceDep = Annotated[AnswerService, Depends(get_answer_service)]
PlayServiceDep = Annotated[PlayService, Depends(get_play_service)]
