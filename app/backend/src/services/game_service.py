from models import Game
from repositories import ClueRepository, GameOptionsRepository, GameRepository
from schemas.game_schema import GameCreate
from services.game_options_service import MAX_GAME_LENGTH, MIN_GAME_LENGTH


class GameService:
    """
    Service for validating and creating a game
    """
    def __init__(
        self,
        game_repo: GameRepository,
        game_options_repo: GameOptionsRepository,
        clue_repo: ClueRepository
    ):
        self.game_repo = game_repo
        self.game_options_repo = game_options_repo
        self.clue_repo = clue_repo

    def _validate_settings(self, settings: GameCreate) -> None:
        """
        Raise ValueError if any chosen setting is not an available option.
        """
        if not MIN_GAME_LENGTH <= settings.num_clues <= MAX_GAME_LENGTH:
            raise ValueError(
                f"Game length must be between {MIN_GAME_LENGTH} and {MAX_GAME_LENGTH}"
            )
        if self.game_options_repo.get_language(settings.language_id) is None:
            raise ValueError("Language does not exist")
        if self.game_options_repo.get_difficulty(settings.difficulty_id) is None:
            raise ValueError("Difficulty does not exist")


    def create_game(
        self, settings: GameCreate, creator_id: int | None = None
    ) -> Game:
        """
        Validate the settings and save a new game (the ruleset only; clues are picked per play).
        Rejects games that could never be played because too few clues exist.
        creator_id stays None until login exists.
        """
        self._validate_settings(settings)

        available = self.clue_repo.count_clues(settings.language_id, settings.difficulty_id)

        if available < settings.num_clues:
            raise ValueError("Not enough clues available for these settings")

        return self.game_repo.add_game(Game(
            num_clues=settings.num_clues,
            language_id=settings.language_id,
            difficulty_id=settings.difficulty_id,
            creator_id=creator_id,
        ))
