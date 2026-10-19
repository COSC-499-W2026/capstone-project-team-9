import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.services.user_service import clear_users

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_users():
    """Start each test with an empty in-memory user list."""
    clear_users()
    yield
    clear_users()


def test_register_user():
    response = client.post(
        "/users/register",
        json={
            "name": "testuser",
            "email": "test@example.com",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "password" not in data
    assert "hashed_password" not in data


def test_duplicate_email():
    first = client.post(
        "/users/register",
        json={
            "name": "firstuser",
            "email": "duplicate@example.com",
            "password": "securepassword123",
        },
    )

    second = client.post(
        "/users/register",
        json={
            "name": "seconduser",
            "email": "duplicate@example.com",
            "password": "securepassword123",
        },
    )

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["detail"] == (
        "Name or email is already registered"
    )


def test_duplicate_name():
    first = client.post(
        "/users/register",
        json={
            "name": "testuser",
            "email": "first@example.com",
            "password": "securepassword123",
        },
    )

    second = client.post(
        "/users/register",
        json={
            "name": "testuser",
            "email": "second@example.com",
            "password": "securepassword123",
        },
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_invalid_email():
    response = client.post(
        "/users/register",
        json={
            "name": "testuser",
            "email": "not-an-email",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 422

    
def test_short_password():
    response = client.post(
        "/users/register",
        json={
            "name": "testuser",
            "email": "test@example.com",
            "password": "short",
        },
    )

    assert response.status_code == 422
