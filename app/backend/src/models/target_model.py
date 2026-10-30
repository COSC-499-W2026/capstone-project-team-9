from datetime import datetime
from sqlmodel import Field, SQLModel, DateTime
from models.location_model import LocationArea

from core.clock import utc_now

class Target(LocationArea, table=True):
    """
    Table for targets. A target has an associated location area and name, and is a created resource.
    """
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    creator_id: int | None = None  # becomes a foreign key once the User model exists
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))
    updated_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))