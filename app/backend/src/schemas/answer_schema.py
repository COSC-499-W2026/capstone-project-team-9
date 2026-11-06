from pydantic import BaseModel


class AnswerResponse(BaseModel):
    correct: bool
    message: str
    attempts: int
    play_complete: bool