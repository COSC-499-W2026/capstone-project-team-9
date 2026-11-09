from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from sqlmodel import Session

from core.dependencies import PlayServiceDep
from schemas.answer_schema import AnswerResponse
from services.play_service import (
    ClueAlreadySolvedError, ClueNotInPlayError, PlayNotFoundError, ClueNotCurrentError
    )

MAX_IMAGE_BYTES = 10 * 1024 * 1024

router = APIRouter(prefix="/plays", tags=["answers"])

# Plain `def` (not async) so the slow OCR runs in FastAPI's threadpool instead of blocking the event loop.
@router.post("/{play_id}/clues/{clue_id}/answer", response_model=AnswerResponse)
def submit_answer(
    play_id: int,
    clue_id: int,
    play_service: PlayServiceDep,
    latitude: float = Form(..., ge=-90, le=90),
    longitude: float = Form(..., ge=-180, le=180),
    image: UploadFile = File(...),
) -> AnswerResponse:
    """Check a photo and the player's location against a clue in their play, and record the attempt."""
    image_bytes = image.file.read(MAX_IMAGE_BYTES + 1)
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Image too large")
    try:
        result = play_service.submit_answer(play_id, clue_id, image_bytes, latitude, longitude)
    except (PlayNotFoundError, ClueNotInPlayError) as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except ClueAlreadySolvedError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    except (ClueAlreadySolvedError, ClueNotCurrentError) as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    except ValueError as exc:  # raised by ocr_service._decode for unreadable images
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    return AnswerResponse(
        correct=result.correct,
        message=result.message,
        attempts=result.attempts,
        play_complete=result.play_complete,
    )