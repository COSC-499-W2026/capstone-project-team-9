from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from models import User
from models.user_model import UserRole

class DuplicateUserError(Exception):
    """Raised when an email address already exists."""

def get_user_by_email(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

def get_all_users(session: Session) -> list[User]:
    return list(session.exec(select(User).order_by(User.name)).all())


def get_user_by_name(session: Session, name: str) -> User | None:
    statement = select(User).where(User.name == name)
    return session.exec(statement).first()


def create_user(
    session: Session,
    *,
    name: str,
    email: str,
    hashed_password: str,
    role: UserRole = UserRole.STUDENT,
) -> User:
    role = UserRole(role)
    user = User(
        name=name,
        email=email,
        hashed_password=hashed_password,
        role=role,
    )

    session.add(user)

    try:
        session.commit()
        session.refresh(user)
    except IntegrityError as exc:
        session.rollback()
        raise DuplicateUserError(
            "Email already exists."
        ) from exc

    return user