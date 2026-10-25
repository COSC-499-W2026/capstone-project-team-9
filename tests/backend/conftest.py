import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from core.docker_guard import ensure_tests_running_in_docker
import models # registers the table models so create_all builds them

ensure_tests_running_in_docker()

@pytest.fixture
def session():
    """A throwaway in-memory database with all tables, fresh for each test."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session



@pytest.fixture
def sample_data():
    """I added this for testing pytests works, will delete when actuall data exsists"""
    return {
        "users": [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
        ],
        "status": "ok",
    }


@pytest.fixture
def mock_api_client(mocker, sample_data):
    """same with this but for mocking, will delete when actual tests exsists"""
    client = mocker.Mock()
    client.get_users.return_value = sample_data["users"]
    client.get_status.return_value = sample_data["status"]
    return client