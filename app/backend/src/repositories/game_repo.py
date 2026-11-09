from models import Game
from repositories import BaseRepository

class GameRepository(BaseRepository):
    """
    Repository class that provides methods for managing Game data.
    """


    def add_game(self, game: Game) -> Game:
        """Save a new game and return it with its generated id."""
        self.session.add(game)
        self.session.commit()
        self.session.refresh(game)
        return game


    def get_game(self, game_id: int) -> Game | None:
        return self.session.get(Game, game_id)