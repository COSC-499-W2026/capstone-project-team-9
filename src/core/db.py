# core/db.py
from sqlmodel import SQLModel, create_engine

# from core.config import settings
import models  # noqa: F401  (registers every table model on SQLModel.metadata)

# engine = create_engine(settings.DATABASE_URL)


def init_db() -> None:
    """Create any missing tables. Called once at startup from main.py's lifespan."""
    # SQLModel.metadata.create_all(engine)
    print("Pretending to create tables")