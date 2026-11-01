from pydantic import BaseModel
from models.location_model import LocationPoint

class LocationCheckRequest(LocationPoint):
    """
    Expected data shape for incoming location check requests
    """
    pass


class LocationCheckResponse(BaseModel):
    allowed: bool
    message: str