from sqlmodel import Session

from models.user_model import User
from repositories.user_repo import get_user_by_email
from services.user_service import verify_password


def authenticate_user(
    session: Session,
    email: str,
    password: str,
) -> User | None:
    """
    Authenticate a user using their email and password.

    Returns the User if authentication succeeds.
    Returns None if the email does not exist or the password is incorrect.
    """
    normalized_email = email.lower()

    user = get_user_by_email(session, normalized_email)

    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user