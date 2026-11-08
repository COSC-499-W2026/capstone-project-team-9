from fastapi import APIRouter

from schemas.location_schema import LocationCheckRequest, LocationCheckResponse
from core.dependencies import LocationServiceDep

router = APIRouter(prefix="/location", tags=["location"])


@router.post("/verify", response_model=LocationCheckResponse)
def verify(body: LocationCheckRequest, location_service: LocationServiceDep) -> LocationCheckResponse:
    # HTTP only: the service fetches the campus location and decides allowed/blocked.
    result = location_service.verify_location(body.latitude, body.longitude)
    return LocationCheckResponse(allowed=result.allowed, message=result.message)