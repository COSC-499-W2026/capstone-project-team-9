from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from core.db import get_session
from core.security import create_access_token, get_current_user
from models.user_model import User
from schemas.login_schema import LoginRequest, TokenResponse
from schemas.user_schema import UserResponse
from services.login_service import authenticate_user


router = APIRouter(prefix="/login", tags=["login"])


@router.post("", response_model=UserResponse)
def login(
    login_data: LoginRequest,
    session: Session = Depends(get_session),
) -> UserResponse:

    user = authenticate_user(
        session=session,
        email=str(login_data.email),
        password=login_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    return UserResponse(
        name=user.name,
        email=user.email,
    )


@router.post("/token", response_model=TokenResponse)
def issue_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> TokenResponse:
    user = authenticate_user(
        session=session,
        email=form_data.username,
        password=form_data.password,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(user.id),
        token_type="bearer",
    )


@router.get("/me", response_model=UserResponse)
def get_logged_in_user(user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(name=user.name, email=user.email)