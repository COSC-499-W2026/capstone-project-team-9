from uuid import uuid4

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from core.docker_guard import ensure_tests_running_in_docker
import models # registers the table models so create_all builds them
from models import Clue, Target

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
def add_clues(session):
    """Factory: add_clues(count, language_id=1, difficulty_id=1) saves clues and returns their ids."""
    def _add(count: int, language_id: int = 1, difficulty_id: int = 1) -> list[int]:
        clue_ids = []
        for _ in range(count):
            target = Target(name=f"target-{uuid4()}", image=b"img")
            session.add(target)
            session.flush()
            clue = Clue(
                audio=b"audio",
                language_id=language_id,
                difficulty_id=difficulty_id,
                target_id=target.id,
            )
            session.add(clue)
            session.flush()
            clue_ids.append(clue.id)
        session.commit()
        return clue_ids
    return _add

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