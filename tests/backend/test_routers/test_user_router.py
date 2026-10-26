import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.db import get_session
from models import User
from routers.user_router import router

@pytest.fixture
def client(session):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = lambda: session
    return TestClient(app)


def test_register_has_value(client, session):
    session.add_all([
        User(
            name="Alice",
            email="alice@example.com",
            hashed_password="hashed_password_1",
        ),
        User(
            name="Bob",
            email="bob@example.com",
            hashed_password="hashed_password_2",
        ),
    ])  
    response = client.get("/users")

    assert response.status_code == 200
    assert response.json() == [
        {"name": "Alice", "email": "alice@example.com"},
        {"name": "Bob", "email": "bob@example.com"},
    ]


def test_invalid_email_returns_422(client):
    response = client.post(
        "/users/register",
        json={
            "name": "Alice",
            "email": "invalid-email",
            "password": "StrongPass123!",
        },
    )

    assert response.status_code == 422


def test_short_password_returns_422(client):
    response = client.post(
        "/users/register",
        json={
            "name": "Alice",
            "email": "alice@example.com",
            "password": "short",
        },
    )

    assert response.status_code == 422


def test_missing_name_returns_422(client):
    response = client.post(
        "/users/register",
        json={
            "email": "alice@example.com",
            "password": "StrongPass123!",
        },
    )

    assert response.status_code == 422