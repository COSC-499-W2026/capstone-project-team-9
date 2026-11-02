from dataclasses import dataclass

from requests import Session

from repositories.target_repo import get_target_by_id
from services.location_service import verify_location_with_target
from services.ocr_service import matches_room
from models.location_model import LocationArea

CORRECT_MESSAGE = "Correct answer!"
WRONG_MESSAGE = "Wrong answer. Try again."

class ClueNotFoundError(Exception):
    """Raised when the clue id doesn't exist."""

@dataclass(frozen=True)
class AnswerResult:
    correct: bool
    message: str

def _room_code(target_name: str) -> str:
    """'COM 201' -> 'COM201', the format the OCR produces."""
    return target_name.replace(" ", "").upper()

def verify_answer(
    session: Session, clue_id: int, image_bytes: bytes, lat: float, lon: float
) -> AnswerResult:
    """Return correct/wrong for the player's photo and location against the clue's target."""
    target = get_target_by_id(session, clue_id)
    if target is None:
        raise ClueNotFoundError("Clue does not exist")
    location = verify_location_with_target(lat, lon, target)
    if not location.allowed:
        return AnswerResult(False, location.message)
    if matches_room(image_bytes, _room_code(target.name)):
        return AnswerResult(True, CORRECT_MESSAGE)
    return AnswerResult(False, WRONG_MESSAGE)