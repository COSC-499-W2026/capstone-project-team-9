from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from core.db import get_session
from core.security import decode_access_token
from models import User
from repositories import ClueRepository
from repositories.user_repo import get_by_id
from services import GameOptionsService, GameService, PlayService

# SESSION DEPENDENCIES -----------------------------------------------------------

SessionDep = Annotated[Session, Depends(get_session)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
) -> User:
    user_id = decode_access_token(token)
    user = get_by_id(session, user_id) if user_id is not None else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]

# REPOSITORY DEPENDENCIES --------------------------------------------------------

def get_clue_repository(session: SessionDep) -> ClueRepository:
    return ClueRepository(session)

ClueRepositoryDep = Annotated[ClueRepository, Depends(get_clue_repository)]

# SERVICE DEPENDENCIES --------------------------------------------------------

def get_game_options_service(
    session: SessionDep,
    clue_repo: ClueRepositoryDep
) -> GameOptionsService:
    return GameOptionsService(session, clue_repo)

def get_game_service(
    session: SessionDep,
    clue_repo: ClueRepositoryDep
) -> GameService:
    return GameService(session, clue_repo)

def get_play_service(
    session: SessionDep,
    clue_repo: ClueRepositoryDep
) -> PlayService:
    return PlayService(session, clue_repo)

GameOptionsServiceDep = Annotated[GameOptionsService, Depends(get_game_options_service)]
GameServiceDep = Annotated[GameService, Depends(get_game_service)]
PlayServiceDep = Annotated[PlayService, Depends(get_play_service)]