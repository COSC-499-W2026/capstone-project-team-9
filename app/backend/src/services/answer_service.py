from dataclasses import dataclass

from services.location_service import TargetLocation, verify_location_with_target
from services.ocr_service import matches_room

CORRECT_MESSAGE = "Correct answer!"
WRONG_MESSAGE = "Wrong answer. Try again."

@dataclass(frozen=True)
class AnswerResult:
    correct: bool
    message: str


def verify_answer(image_bytes: bytes, lat: float, lon: float, expected_room: str, target_location: TargetLocation) -> AnswerResult:
    """Return correct/wrong for the player's answer."""
    location = verify_location_with_target(lat, lon, target_location)
    if not location.allowed:
        return AnswerResult(False, location.message)
    if matches_room(image_bytes, expected_room):
        return AnswerResult(True, CORRECT_MESSAGE)
    return AnswerResult(False, WRONG_MESSAGE)