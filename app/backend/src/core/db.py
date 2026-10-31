# core/db.py
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from collections.abc import Iterator
import os
import models # this import looks unused, but registers every table model on SQLModel.metadata

engine = create_engine(os.getenv("DATABASE_URL"))


def init_db() -> None:
    """Create any missing tables"""
    SQLModel.metadata.create_all(engine)

def drop_db() -> None:
    """For dev environment use only. Drops all tables. BE CAREFUL!"""
    if os.getenv("ENV") == "development":
        SQLModel.metadata.drop_all(engine)

def get_session() -> Iterator[Session]:
    """FastAPI dependency: one DB session per request, closed afterwards."""
    with Session(engine) as session:
        yield session

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()