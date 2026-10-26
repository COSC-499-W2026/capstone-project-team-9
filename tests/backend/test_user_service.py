import pytest
import bcrypt
from unittest.mock import MagicMock

from services.user_service import hash_password, register_user
from repositories.user_repo import User, DuplicateUserError
from schemas.user_schema import UserCreate

def test_hash_password():
    password = "hashed_password_1"

    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$2b$12$")

    assert bcrypt.checkpw(
        password.encode("utf-8"),
        hashed.encode("utf-8"),
    )


def test_hash_password_uses_different_salts():
    password = "hashed_password_1"

    hash1 = hash_password(password)
    hash2 = hash_password(password)

    assert hash1 != hash2

    assert bcrypt.checkpw(
        password.encode("utf-8"),
        hash1.encode("utf-8"),
    )
    assert bcrypt.checkpw(
        password.encode("utf-8"),
        hash2.encode("utf-8"),
    )


def test_register_user_success(monkeypatch):
    session = MagicMock()

    user_data = UserCreate(
        name="Alice",
        email="alice@example.com",
        password="hashed_password_1",
    )

    monkeypatch.setattr(
        "services.user_service.user_repo.get_user_by_name",
        lambda session, name: None,
    )

    monkeypatch.setattr(
        "services.user_service.user_repo.get_user_by_email",
        lambda session, email: None,
    )

    def fake_create_user(
        session,
        *,
        name,
        email,
        hashed_password,
    ):
        from models.user_model import User

        return User(
            name=name,
            email=email,
            hashed_password=hashed_password,
        )

    monkeypatch.setattr(
        "services.user_service.user_repo.create_user",
        fake_create_user,
    )

    user = register_user(session, user_data)

    assert user.name == "Alice"
    assert user.email == "alice@example.com"
    assert user.hashed_password != "hashed_password_1"


def test_register_user_normalizes_email(monkeypatch):
    session = MagicMock()

    user_data = UserCreate(
        name="Alice",
        email="ALICE@EXAMPLE.COM",
        password="hashed_password_1",
    )

    monkeypatch.setattr(
        "services.user_service.user_repo.get_user_by_name",
        lambda session, name: None,
    )

    monkeypatch.setattr(
        "services.user_service.user_repo.get_user_by_email",
        lambda session, email: None,
    )

    def fake_create_user(
        session,
        *,
        name,
        email,
        hashed_password,
    ):
        from models.user_model import User

        return User(
            name=name,
            email=email,
            hashed_password=hashed_password,
        )

    monkeypatch.setattr(
        "services.user_service.user_repo.create_user",
        fake_create_user,
    )

    user = register_user(session, user_data)

    assert user.email == "alice@example.com"


def test_register_user_duplicate_name(monkeypatch):
    session = MagicMock()

    user_data = UserCreate(
        name="Alice",
        email="alice@example.com",
        password="hashed_password_1",
    )

    monkeypatch.setattr(
        "services.user_service.user_repo.get_user_by_name",
        lambda session, name: object(),
    )

    def fail_if_created(*args, **kwargs):
        pytest.fail("create_user should not be called for a duplicate username")

    monkeypatch.setattr(
        "services.user_service.user_repo.create_user",
        fail_if_created,
    )

    with pytest.raises(DuplicateUserError) as exc_info:
        register_user(session, user_data)

    assert str(exc_info.value) == "Username already exists."


def test_register_user_duplicate_email(monkeypatch):
    session = MagicMock()

    user_data = UserCreate(
        name="Alice",
        email="alice@example.com",
        password="hashed_password_1",
    )

    monkeypatch.setattr(
        "services.user_service.user_repo.get_user_by_name",
        lambda session, name: None,
    )

    monkeypatch.setattr(
        "services.user_service.user_repo.get_user_by_email",
        lambda session, email: object(),
    )

    def fail_if_created(*args, **kwargs):
        pytest.fail("create_user should not be called for a duplicate email")

    monkeypatch.setattr(
        "services.user_service.user_repo.create_user",
        fail_if_created,
    )

    with pytest.raises(DuplicateUserError) as exc_info:
        register_user(session, user_data)

    assert str(exc_info.value) == "Email is already registered."