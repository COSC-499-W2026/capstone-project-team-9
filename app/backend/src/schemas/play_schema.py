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