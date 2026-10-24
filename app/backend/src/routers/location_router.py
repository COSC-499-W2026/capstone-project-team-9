from fastapi import APIRouter

from schemas.location_schema import LocationCheckRequest, LocationCheckResponse
from services.location_service import verify_location

router = APIRouter(prefix="/location", tags=["location"])


@router.post("/verify", response_model=LocationCheckResponse)
def verify(body: LocationCheckRequest) -> LocationCheckResponse:
    # HTTP only: the service fetches the campus location and decides allowed/blocked.
    result = verify_location(body.latitude, body.longitude)
    return LocationCheckResponse(allowed=result.allowed, message=result.message)