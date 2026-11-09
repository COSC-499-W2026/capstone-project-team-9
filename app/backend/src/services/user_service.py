from sqlmodel import Session

from core.security import hash_password
from models.user_model import User, UserRole
from repositories import user_repo
from repositories.user_repo import DuplicateUserError
from schemas.user_schema import UserCreate


def register_user(session: Session, user_data: UserCreate) -> User:
    email = str(user_data.email).lower()

    if user_repo.get_user_by_email(session, email):
        raise DuplicateUserError("Email is already registered.")

    hashed_password = hash_password(user_data.password)

    return user_repo.create_user(
        session,
        name=user_data.name,
        email=email,
        hashed_password=hashed_password,
        role=UserRole.STUDENT,
    )