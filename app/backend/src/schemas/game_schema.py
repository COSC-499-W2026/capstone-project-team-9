from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GameCreate(BaseModel):
    language_id: int
    difficulty_id: int
    num_clues: int = Field(gt=0)


class GameResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    language_id: int
    difficulty_id: int
    num_clues: int
    created_at: datetime


class ClueResponse(BaseModel):
    id: int


class GameStartResponse(BaseModel):
    game: GameResponse
    clues: list[ClueResponse]