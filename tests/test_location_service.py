import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.repositories.location_repo import get_campus_polygons
from src.routers.location_router import router
from src.services.location_service import BLOCKED_MESSAGE, verify_location

# A small fake campus, so these tests don't depend on the real boundary data
# (and keep working unchanged once the boundary lives in the database).
# Points are (lat, lon).
TEST_CAMPUS = [[(49.93, -119.40), (49.93, -119.39), (49.94, -119.39), (49.94, -119.40)]]
ON_CAMPUS = (49.935, -119.395)
OFF_CAMPUS = [(49.8880, -119.4960), (49.2827, -123.1207), (0.0, 0.0), (49.95, -119.395)]


def test_on_campus_allows_start():
    assert verify_location(*ON_CAMPUS, TEST_CAMPUS).allowed is True


@pytest.mark.parametrize("lat,lon", OFF_CAMPUS)
def test_off_campus_blocks_start_with_message(lat, lon):
    result = verify_location(lat, lon, TEST_CAMPUS)
    assert result.allowed is False
    assert result.message == BLOCKED_MESSAGE


def test_no_boundary_data_blocks():
    assert verify_location(*ON_CAMPUS, []).allowed is False


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    # DB NOTE: this override is what keeps endpoint tests database-free later.
    app.dependency_overrides[get_campus_polygons] = lambda: TEST_CAMPUS
    return TestClient(app)


def test_endpoint_on_campus(client):
    r = client.post("/location/verify", json={"latitude": ON_CAMPUS[0], "longitude": ON_CAMPUS[1]})
    assert r.status_code == 200 and r.json()["allowed"] is True


def test_endpoint_off_campus(client):
    r = client.post("/location/verify", json={"latitude": 49.2827, "longitude": -123.1207})
    assert r.status_code == 200
    assert r.json() == {"allowed": False, "message": BLOCKED_MESSAGE}


def test_endpoint_rejects_invalid_coordinates(client):
    r = client.post("/location/verify", json={"latitude": 200, "longitude": 0})
    assert r.status_code == 422


# FILE-ONLY: replace with a test against the DB (or delete) when the table exists.
def test_file_boundary_loads_and_contains_a_ring():
    rings = get_campus_polygons()
    assert len(rings) >= 1 and len(rings[0]) >= 4