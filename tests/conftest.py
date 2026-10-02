import pytest


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
    """same with this but for mocking"""
    client = mocker.Mock()
    client.get_users.return_value = sample_data["users"]
    client.get_status.return_value = sample_data["status"]
    return client