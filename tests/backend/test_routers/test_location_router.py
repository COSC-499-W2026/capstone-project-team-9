import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from routers.location_router import router
from services.location_service import LocationResult


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_verify_returns_200_with_allowed_result(client, monkeypatch):
    monkeypatch.setattr(
        "routers.location_router.verify_location", lambda lat, lon: LocationResult(True, "ok")
    )
    r = client.post("/location/verify", json={"latitude": 49.9, "longitude": -119.4})
    assert r.status_code == 200
    assert r.json() == {"allowed": True, "message": "ok"}


def test_verify_returns_200_when_blocked(client, monkeypatch):
    monkeypatch.setattr(
        "routers.location_router.verify_location", lambda lat, lon: LocationResult(False, "no")
    )
    r = client.post("/location/verify", json={"latitude": 0, "longitude": 0})
    assert r.status_code == 200
    assert r.json() == {"allowed": False, "message": "no"}


def test_verify_passes_coordinates_to_service(client, monkeypatch):
    seen = {}

    def fake(lat, lon):
        seen["args"] = (lat, lon)
        return LocationResult(True, "ok")

    monkeypatch.setattr("routers.location_router.verify_location", fake)
    client.post("/location/verify", json={"latitude": 49.9, "longitude": -119.4})
    assert seen["args"] == (49.9, -119.4)


@pytest.mark.parametrize("body", [{"latitude": 200, "longitude": 0}, {"latitude": 0, "longitude": 500}, {}])
def test_verify_rejects_invalid_input(client, body):
    assert client.post("/location/verify", json=body).status_code == 422