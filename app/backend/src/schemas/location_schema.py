from pydantic import BaseModel, Field


class LocationCheckRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class LocationCheckResponse(BaseModel):
    allowed: bool
    message: str