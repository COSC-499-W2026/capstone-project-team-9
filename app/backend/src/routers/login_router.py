from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from core.db import get_session
from schemas.login_schema import LoginRequest
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
        role=user.role,
    )