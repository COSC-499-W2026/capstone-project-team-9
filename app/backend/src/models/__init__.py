"""Import every table model here so SQLModel registers it.

A table missing from this file will not be created by `scripts/init_db.py`
"""

from .language_model import Language
from .difficulty_model import Difficulty
from .clue_model import Clue
from .target_model import Target
from .game_model import Game