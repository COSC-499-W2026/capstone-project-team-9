import pytest
from fastapi.testclient import TestClient

from main import app
from services.user_service import clear_user

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_user():
    """Start each test with an empty in-memory user list."""
    clear_user()
    yield
    clear_user()


def test_register_user():
    response = client.post(
        "/user/register",
        json={
            "name": "testuser",
            "email": "test@example.com",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "password" not in data
    assert "hashed_password" not in data


def test_duplicate_email():
    first = client.post(
        "/user/register",
        json={
            "name": "firstuser",
            "email": "duplicate@example.com",
            "password": "securepassword123",
        },
    )

    second = client.post(
        "/user/register",
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
        "/user/register",
        json={
            "name": "testuser",
            "email": "first@example.com",
            "password": "securepassword123",
        },
    )

    second = client.post(
        "/user/register",
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
        "/user/register",
        json={
            "name": "testuser",
            "email": "not-an-email",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 422

    
def test_short_password():
    response = client.post(
        "/user/register",
        json={
            "name": "testuser",
            "email": "test@example.com",
            "password": "short",
        },
    )

    assert response.status_code == 422