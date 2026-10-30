"""
Should not contain a table. 
Only contains shared models for defining locations, inherited by schemas and other models.
"""
from sqlmodel import SQLModel, Field

class LocationPoint(SQLModel):
    """
    Defines a location as a point (`latitude, longitude`)
    """
    latitude:  float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)