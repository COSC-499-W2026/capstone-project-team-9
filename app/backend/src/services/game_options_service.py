from dataclasses import dataclass

from models import Difficulty, Language
from repositories import ClueRepository, GameOptionsRepository

# TODO: confirm the max with the client
MIN_GAME_LENGTH = 1
MAX_GAME_LENGTH = 10


@dataclass(frozen=True)
class GameLengthRange:
    min: int
    max: int


class GameOptionsService:
    """
    Service for processing "Get game options": what a player can pick when creating a game.
    """
    def __init__(self, game_options_repo: GameOptionsRepository, clue_repo: ClueRepository):
        self.game_options_repo = game_options_repo
        self.clue_repo = clue_repo

    def list_languages(self) -> list[Language]:
        return self.game_options_repo.get_all_languages()


    def list_difficulties(self) -> list[Difficulty]:
        return self.game_options_repo.get_all_difficulties()


    def get_game_length_range(self, language_id: int, difficulty_id: int) -> GameLengthRange:
        """
        Playable game lengths for this combo. (0, 0) means no game can be made.
        """
        available = self.clue_repo.count_clues(language_id, difficulty_id)

        if available == 0:
            return GameLengthRange(0, 0)

        return GameLengthRange(MIN_GAME_LENGTH, min(MAX_GAME_LENGTH, available))