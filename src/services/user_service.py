import hashlib
import secrets

from models.user_model import User
from repositories import user_repo
from repositories.user_repo import DuplicateUserError
from schemas.user_schema import UserCreate

users: list[dict] = []


def hash_password(password: str) -> str:
    """Hash a password without requiring an external library."""
    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        600_000,
    )

    return f"{salt.hex()}:{password_hash.hex()}"


def register_user(user_data: UserCreate) -> User:
    email = str(user_data.email).lower()

    if user_repo.get_user_by_name(user_data.name):
        raise DuplicateUserError("Username already exists.")
    
    if user_repo.get_user_by_email(email):
        raise DuplicateUserError("Email is already registered.")

    hashed_password = hash_password(user_data.password)

    return user_repo.create_user(
        name=user_data.name,
        email=email,
        hashed_password=hashed_password,
    )