from dataclasses import dataclass

from sqlmodel import Session

from repositories import TargetRepository
from services import LocationService
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


class AnswerService:
    """
    Service for checking users' submitted answers with actual targets
    """

    def __init__(self, location_service: LocationService, target_repo: TargetRepository):
        self.location_service = location_service
        self.target_repo = target_repo

    def verify_answer(
        self, clue_id: int, image_bytes: bytes, lat: float, lon: float
    ) -> AnswerResult:
        """
        Return correct/wrong for the player's photo and location against the clue's target.
        """

        target = self.target_repo.get_target_for_clue(session, clue_id)

        if target is None:
            raise ClueNotFoundError("Clue does not exist")

        location = self.location_service.verify_location_with_target(lat, lon, target)

        if not location.allowed:
            return AnswerResult(False, location.message)

        if matches_room(image_bytes, _room_code(target.name)):
            return AnswerResult(True, CORRECT_MESSAGE)

        return AnswerResult(False, WRONG_MESSAGE)