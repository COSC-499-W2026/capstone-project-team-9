import hashlib
import secrets

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


def register_user(user_data: UserCreate) -> dict:
    normalized_email = str(user_data.email).lower()

    for user in users:
        if (
            user["name"].lower() == user_data.name.lower()
            or user["email"].lower() == normalized_email
        ):
            raise ValueError("Name or email is already registered")

    new_user = {
        "name": user_data.name,
        "email": normalized_email,
        "hashed_password": hash_password(user_data.password)
    }

    users.append(new_user)

    return new_user.copy()


def clear_user() -> None:
    """Reset temporary data for testing."""
    users.clear()