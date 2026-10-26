"""Persistence for the Game table."""
from sqlmodel import Session

from models import Game


def add_game(session: Session, game: Game) -> Game:
    """Save a new game and return it with its generated id."""
    session.add(game)
    session.commit()
    session.refresh(game)
    return game