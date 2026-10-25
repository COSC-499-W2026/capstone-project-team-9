from pydantic import BaseModel, ConfigDict


class LanguageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class DifficultyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str

class GameLengthResponse(BaseModel):
    min : int
    max : int