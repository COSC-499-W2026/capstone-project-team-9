from fastapi import Depends
from sqlmodel import Session
from core.db import get_session
from repositories.clue_repo import ClueRepository

def get_clue_repository(session: Session = Depends(get_session)) -> ClueRepository:
    return ClueRepository(session)