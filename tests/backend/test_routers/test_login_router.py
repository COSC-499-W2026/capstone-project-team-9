import hashlib
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jwcrypto import jwe, jwk
from jwcrypto.common import base64url_decode, base64url_encode

import core.security
from core.db import get_session
from core.security import (
    ACCESS_TOKEN_EXPIRE_SECONDS,
    decode_access_token,
    create_access_token,
)
from models.user_model import User
from repositories.user_repo import create_user
from routers.login_router import router
from services.user_service import hash_password



@pytest.fixture
def client(session):
    app = FastAPI()
    app.include_router(router)

    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def user(session):
    return create_user(
        session,
        name="Alice",
        email="alice@example.com",
        hashed_password=hash_password("StrongPass123!"),
    )


def test_login_success(client, user):
    response = client.post(
        "/login",
        json={
            "email": "alice@example.com",
            "password": "StrongPass123!",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "name": "Alice",
        "email": "alice@example.com",
    }


def test_oauth2_token_authenticates_user(client, user, monkeypatch):
    monkeypatch.setenv("AUTH_TOKEN_SECRET", "test-secret-with-at-least-32-characters")

    response = client.post(
        "/login/token",
        data={"username": "alice@example.com", "password": "StrongPass123!"},
    )

    assert response.status_code == 200
    token = response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"

    current_user = client.get(
        "/login/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert current_user.status_code == 200
    assert current_user.json() == {"name": "Alice", "email": "alice@example.com"}


def test_access_token_is_encrypted_jwt(user, monkeypatch):
    secret = "test-secret-with-at-least-32-characters"
    monkeypatch.setenv("AUTH_TOKEN_SECRET", secret)

    token = create_access_token(user.id)
    parts = token.split(".")
    assert len(parts) == 5
    header = json.loads(base64url_decode(parts[0]))
    assert header == {"alg": "dir", "enc": "A256GCM", "typ": "JWT"}

    key = hashlib.sha256(secret.encode()).digest()
    encrypted_token = jwe.JWE()
    encrypted_token.deserialize(
        token,
        key=jwk.JWK(kty="oct", k=base64url_encode(key)),
    )
    payload = json.loads(encrypted_token.payload)
    assert payload["sub"] == str(user.id)
    assert payload["exp"] > core.security.time.time()
    assert decode_access_token(token) == user.id


@pytest.mark.parametrize("secret", [None, "too-short"])
@pytest.mark.parametrize(
    "operation",
    [lambda: create_access_token(1), lambda: decode_access_token("a.b.c")],
)
def test_token_operations_require_long_authentication_secret(
    monkeypatch, secret, operation
):
    if secret is None:
        monkeypatch.delenv("AUTH_TOKEN_SECRET", raising=False)
    else:
        monkeypatch.setenv("AUTH_TOKEN_SECRET", secret)

    with pytest.raises(RuntimeError, match="AUTH_TOKEN_SECRET must be set"):
        operation()


def test_oauth2_token_rejects_invalid_password(client, user, monkeypatch):
    monkeypatch.setenv("AUTH_TOKEN_SECRET", "test-secret-with-at-least-32-characters")

    response = client.post(
        "/login/token",
        data={"username": "alice@example.com", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_rejects_tampered_token(client, user, monkeypatch):
    monkeypatch.setenv("AUTH_TOKEN_SECRET", "test-secret-with-at-least-32-characters")
    parts = create_access_token(user.id).split(".")
    parts[3] = ("A" if parts[3][0] != "A" else "B") + parts[3][1:]

    response = client.get(
        "/login/me",
        headers={"Authorization": f"Bearer {'.'.join(parts)}"},
    )

    assert response.status_code == 401


def test_me_rejects_expired_token(client, user, monkeypatch):
    monkeypatch.setenv("AUTH_TOKEN_SECRET", "test-secret-with-at-least-32-characters")
    monkeypatch.setattr(core.security.time, "time", lambda: 1000)
    token = create_access_token(user.id)
    monkeypatch.setattr(
        core.security.time,
        "time",
        lambda: 1000 + ACCESS_TOKEN_EXPIRE_SECONDS,
    )

    response = client.get(
        "/login/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


@pytest.mark.parametrize("authorization", [None, "Bearer invalid-token"])
def test_me_rejects_missing_or_invalid_token(client, monkeypatch, authorization):
    monkeypatch.setenv("AUTH_TOKEN_SECRET", "test-secret-with-at-least-32-characters")
    headers = {} if authorization is None else {"Authorization": authorization}

    response = client.get("/login/me", headers=headers)

    assert response.status_code == 401


def test_login_wrong_password(client, user):
    response = client.post(
        "/login",
        json={
            "email": "alice@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid email or password."
    }


def test_login_unknown_email(client):
    response = client.post(
        "/login",
        json={
            "email": "unknown@example.com",
            "password": "StrongPass123!",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid email or password."
    }


def test_login_invalid_email_format(client):
    response = client.post(
        "/login",
        json={
            "email": "not-an-email",
            "password": "StrongPass123!",
        },
    )

    assert response.status_code == 422


def test_login_missing_password(client):
    response = client.post(
        "/login",
        json={
            "email": "alice@example.com",
        },
    )

    assert response.status_code == 422


def test_login_missing_email(client):
    response = client.post(
        "/login",
        json={
            "password": "StrongPass123!",
        },
    )

    assert response.status_code == 422


def test_login_empty_password(client):
    response = client.post(
        "/login",
        json={
            "email": "alice@example.com",
            "password": "",
        },
    )

    assert response.status_code == 422