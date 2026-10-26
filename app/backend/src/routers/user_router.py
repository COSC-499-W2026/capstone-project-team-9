from fastapi import APIRouter, HTTPException, status

from repositories.user_repo import DuplicateUserError
from schemas.user_schema import UserCreate, UserResponse
from services.user_service import register_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate) -> UserResponse:
    try:
        user = register_user(user_data)
    except DuplicateUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return UserResponse(
        name=user.name,
        email=user.email,
    )