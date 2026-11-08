import base64
import hashlib
import hmac
import json
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


def _encode_segment(value: dict[str, str | int]) -> str:
    encoded = json.dumps(value, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(encoded).decode().rstrip("=")


def _decode_segment(segment: str) -> dict:
    decoded = base64.b64decode(
        segment + "=" * (-len(segment) % 4),
        altchars=b"-_",
        validate=True,
    )
    value = json.loads(decoded)
    if not isinstance(value, dict):
        raise ValueError("JWT segment must contain a JSON object.")
    return value


def _token_secret() -> bytes:
    secret = os.getenv("AUTH_TOKEN_SECRET")
    if not secret or len(secret.encode("utf-8")) < 32:
        raise RuntimeError("AUTH_TOKEN_SECRET must be set to at least 32 characters.")
    return secret.encode("utf-8")


def create_access_token(user_id: int) -> str:
    header = _encode_segment({"alg": "HS256", "typ": "JWT"})
    payload = _encode_segment(
        {
            "sub": str(user_id),
            "exp": int(time.time()) + ACCESS_TOKEN_EXPIRE_SECONDS,
        }
    )
    message = f"{header}.{payload}"
    signature = hmac.new(_token_secret(), message.encode(), hashlib.sha256)
    encoded_signature = base64.urlsafe_b64encode(signature.digest()).decode().rstrip("=")
    return f"{message}.{encoded_signature}"


def _get_token_user_id(token: str) -> int | None:
    secret = _token_secret()
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
        header = _decode_segment(encoded_header)
        if header.get("alg") != "HS256" or header.get("typ") != "JWT":
            return None

        message = f"{encoded_header}.{encoded_payload}"
        expected_signature = hmac.new(
            secret, message.encode(), hashlib.sha256
        ).digest()
        signature = base64.b64decode(
            encoded_signature + "=" * (-len(encoded_signature) % 4),
            altchars=b"-_",
            validate=True,
        )
        if not hmac.compare_digest(signature, expected_signature):
            return None

        payload = _decode_segment(encoded_payload)
        user_id = int(payload["sub"])
        expires_at = int(payload["exp"])
        if user_id <= 0 or expires_at <= time.time():
            return None
        return user_id
    except (KeyError, TypeError, ValueError, UnicodeDecodeError):
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
