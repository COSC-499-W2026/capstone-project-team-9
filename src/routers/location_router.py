from fastapi import APIRouter, Depends

from src.repositories.location_repo import Ring, get_campus_polygons
from src.schemas.location_schema import LocationCheckRequest, LocationCheckResponse
from src.services.location_service import verify_location

router = APIRouter(prefix="/location", tags=["location"])


@router.post("/verify", response_model=LocationCheckResponse)
def verify(
    body: LocationCheckRequest,
    # DB NOTE: this line does not change when the database arrives. Once
    # get_campus_polygons takes a session (see location_repo.py), FastAPI
    # injects it automatically through this Depends.
    rings: list[Ring] = Depends(get_campus_polygons),
) -> LocationCheckResponse:
    result = verify_location(body.latitude, body.longitude, rings)
    return LocationCheckResponse(allowed=result.allowed, message=result.message)