from sqlmodel import Session

from core.security import verify_password
from models.user_model import User
from repositories.user_repo import get_user_by_email


def authenticate_user(
    session: Session,
    email: str,
    password: str,
) -> User | None:
    normalized_email = email.lower()

    user = get_user_by_email(session, normalized_email)

    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user