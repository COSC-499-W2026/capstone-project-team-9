import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.dependencies import get_location_service
from routers.location_router import router
from services.location_service import LocationResult, LocationService


@pytest.fixture
def location_service(mocker):
    return mocker.create_autospec(LocationService, instance=True)


@pytest.fixture
def client(location_service):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_location_service] = lambda: location_service
    return TestClient(app)


def test_verify_returns_200_with_allowed_result(client, location_service):
    location_service.verify_location.return_value = LocationResult(True, "ok")

    r = client.post("/location/verify", json={"latitude": 49.9, "longitude": -119.4})
    assert r.status_code == 200
    assert r.json() == {"allowed": True, "message": "ok"}


def test_verify_returns_200_when_blocked(client, location_service):
    location_service.verify_location.return_value = LocationResult(False, "no")

    r = client.post("/location/verify", json={"latitude": 0, "longitude": 0})
    assert r.status_code == 200
    assert r.json() == {"allowed": False, "message": "no"}


def test_verify_passes_coordinates_to_service(client, location_service):
    location_service.verify_location.return_value = LocationResult(True, "ok")

    client.post("/location/verify", json={"latitude": 49.9, "longitude": -119.4})

    location_service.verify_location.assert_called_once_with(49.9, -119.4)


@pytest.mark.parametrize("body", [{"latitude": 200, "longitude": 0}, {"latitude": 0, "longitude": 500}, {}])
def test_verify_rejects_invalid_input(client, location_service, body):
    assert client.post("/location/verify", json=body).status_code == 422
    location_service.verify_location.assert_not_called()