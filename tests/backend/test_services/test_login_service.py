import pytest
from sqlmodel import SQLModel, Session, create_engine

from models.user_model import User
from repositories.user_repo import create_user
from services.login_service import authenticate_user
from services.user_service import hash_password


@pytest.fixture
def user(session):
    """Create a user in the test database."""
    return create_user(
        session,
        name="Alice",
        email="alice@example.com",
        hashed_password=hash_password("StrongPass123!"),
    )


def test_authenticate_user_success(session, user):
    """Valid credentials should return the user."""
    result = authenticate_user(
        session,
        "alice@example.com",
        "StrongPass123!",
    )

    assert result is not None
    assert result.id == user.id
    assert result.name == "Alice"
    assert result.email == "alice@example.com"


def test_authenticate_user_wrong_password(session, user):
    """An incorrect password should return None."""
    result = authenticate_user(
        session,
        "alice@example.com",
        "WrongPassword123!",
    )

    assert result is None


def test_authenticate_user_email_not_found(session):
    """An unknown email should return None."""
    result = authenticate_user(
        session,
        "unknown@example.com",
        "StrongPass123!",
    )

    assert result is None


def test_authenticate_user_normalizes_email(session, user):
    """An uppercase email should be normalized before lookup."""
    result = authenticate_user(
        session,
        "ALICE@EXAMPLE.COM",
        "StrongPass123!",
    )

    assert result is not None
    assert result.id == user.id