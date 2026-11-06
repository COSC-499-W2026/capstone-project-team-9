from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlayResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    game_id: int
    started_at: datetime


class ClueResponse(BaseModel):
    id: int


class PlayStartResponse(BaseModel):
    play: PlayResponse
    clues: list[ClueResponse]

class PlayClueState(BaseModel):
    clue_id: int
    position: int  # for ordering only: skipping will leave gaps, so don't show this as "question N"
    solved: bool
    attempts: int


class PlayStateResponse(BaseModel):
    id: int
    game_id: int | None
    completed: bool
    current_clue_id: int | None
    total_clues: int
    solved_clues: int