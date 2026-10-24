# core/db.py
from sqlmodel import SQLModel, create_engine
import os
import models # this import looks unused, but registers every table model on SQLModel.metadata

engine = create_engine(os.getenv("DATABASE_URL"))


def init_db() -> None:
    """Create any missing tables"""
    SQLModel.metadata.create_all(engine)