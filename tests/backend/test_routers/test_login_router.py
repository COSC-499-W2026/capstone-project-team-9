import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.db import get_session
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