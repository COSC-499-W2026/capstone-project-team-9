from sqlmodel import Session
import bcrypt

from models.user_model import User
from repositories import user_repo
from repositories.user_repo import DuplicateUserError
from schemas.user_schema import UserCreate


def hash_password(password: str) -> str:
    """Securely hash a password using bcrypt."""
    password_bytes = password.encode("utf-8")

    hashed_password = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(rounds=12),
    )

    return hashed_password.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its stored bcrypt hash."""
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def register_user(session: Session, user_data: UserCreate) -> User:
    email = str(user_data.email).lower()

    if user_repo.get_user_by_name(session, user_data.name):
        raise DuplicateUserError("Username already exists.")

    if user_repo.get_user_by_email(session, email):
        raise DuplicateUserError("Email is already registered.")

    hashed_password = hash_password(user_data.password)

    return user_repo.create_user(
        session,
        name=user_data.name,
        email=email,
        hashed_password=hashed_password,
    )