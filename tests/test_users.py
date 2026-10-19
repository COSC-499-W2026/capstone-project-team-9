import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session, create_engine

from src.database import get_db
from src.main import app

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    pytest.skip(
        "Set TEST_DATABASE_URL to run PostgreSQL integration tests", 
        allow_module_level=True,
)

test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)


def override_get_db():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_users_table():
    with test_engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS users"))
        connection.execute(
            text(
                """
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    hashed_password TEXT NOT NULL
                )
                """
            )
        )

    yield

    with test_engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS users"))


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
assert data["name"] == "testuser"
assert data["email"] == "test@example.com"
assert "hashed_password" not in data
assert "password" not in data


def test_duplicate_email():
    payload = {
        "name": "firstuser",
        "email": "duplicate@example.com",
        "password": "securepassword123",
    }

    first = client.post("/users/register", json=payload)
    second = client.post(
        "/users/register",
        json={
            **payload,
            "name": "seconduser",
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