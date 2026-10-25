from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from models.user_model import User

_users: list[User] = []

class DuplicateUserError(Exception):
    """Raised when a username or email already exists."""

def get_user_by_email(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

def get_all_users() -> list[User]:
    return list(_users)


def get_user_by_name(name: str) -> User | None:
    for user in _users:
        if user.name == name:
            return user
    return None


def get_user_by_email(email: str) -> User | None:
    normalized_email = email.lower()

    for user in _users:
        if user.email.lower() == normalized_email:
            return user
    return None

def create_user(
    session: Session,
    *,
    name: str,
    email: str,
    hashed_password: str,
) -> User:
    user = User(
        name=name,
        email=email,
        hashed_password=hashed_password,
    )

    session.add(user)

    try:
        session.commit()
        session.refresh(user)
    except IntegrityError as exc:
        session.rollback()
        raise DuplicateUserError(
        ) from exc

    return user