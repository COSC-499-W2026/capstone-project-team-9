from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from core.db import get_session
from repositories.user_repo import DuplicateUserError, get_all_users
from schemas.user_schema import UserCreate, UserResponse
from services.user_service import register_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, session: Session = Depends(get_session)) -> UserResponse:
    try:
        user = register_user(session, user_data)
    except DuplicateUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return UserResponse(
        name=user.name,
        email=user.email,
    )

@router.get("", response_model=list[UserResponse])
def list_users(
    session: Session = Depends(get_session),
    ) -> list[UserResponse]:
    users = get_all_users(session)

    return [
        UserResponse(
            name=user.name,
            email=user.email,
        )
        for user in users
    ]