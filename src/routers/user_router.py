from fastapi import APIRouter, HTTPException, status

from schemas.user_schema import UserCreate, UserResponse
from services.user_service import register_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(user_data: UserCreate):
    try:
        return register_user(user_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )from exc
