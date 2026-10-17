import pytest
import os
import sys

if os.getenv("RUNNING_IN_DOCKER") != "true":
    print(
        "\n🛑 STOP! You are trying to run tests on your host machine.\n" +
        "Tests must be run inside Docker to ensure environment parity.\n" +
        "👉 Run this instead:\n\n" +
        "    docker compose exec backend pytest\n"
    )
    sys.exit(1)

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