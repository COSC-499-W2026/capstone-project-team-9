import base64
import hashlib
import hmac
import os
import time
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from core.db import get_session
from models.user_model import User

ACCESS_TOKEN_EXPIRE_SECONDS = 1800
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")


def _token_secret() -> bytes:
    secret = os.getenv("AUTH_TOKEN_SECRET")
    if not secret or len(secret.encode("utf-8")) < 32:
        raise RuntimeError("AUTH_TOKEN_SECRET must be set to at least 32 characters.")
    return secret.encode("utf-8")


def create_access_token(user_id: int) -> str:
    payload = f"{user_id}:{int(time.time()) + ACCESS_TOKEN_EXPIRE_SECONDS}".encode()
    encoded_payload = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = hmac.new(_token_secret(), encoded_payload.encode(), hashlib.sha256)
    encoded_signature = base64.urlsafe_b64encode(signature.digest()).decode().rstrip("=")
    return f"{encoded_payload}.{encoded_signature}"


def _get_token_user_id(token: str) -> int | None:
    try:
        encoded_payload, encoded_signature = token.split(".")
        expected_signature = hmac.new(
            _token_secret(), encoded_payload.encode(), hashlib.sha256
        ).digest()
        signature = base64.urlsafe_b64decode(
            encoded_signature + "=" * (-len(encoded_signature) % 4)
        )
        if not hmac.compare_digest(signature, expected_signature):
            return None

        payload = base64.urlsafe_b64decode(
            encoded_payload + "=" * (-len(encoded_payload) % 4)
        ).decode()
        user_id, expires_at = (int(value) for value in payload.split(":"))
        if user_id <= 0 or expires_at <= time.time():
            return None
        return user_id
    except (ValueError, UnicodeDecodeError):
        return None


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> User:
    user_id = _get_token_user_id(token)
    user = session.get(User, user_id) if user_id is not None else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
