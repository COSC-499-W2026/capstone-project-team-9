from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlmodel import Session

from core.db import get_session
from services.answer_service import ClueNotFoundError, AnswerResult, verify_answer

MAX_IMAGE_BYTES = 10 * 1024 * 1024

router = APIRouter(prefix="/answers", tags=["answers"])

# Plain `def` (not async) so the slow OCR runs in FastAPI's threadpool instead of blocking the event loop.
@router.post("/verify", response_model=AnswerResult)
def verify(
    clue_id: int = Form(...),
    latitude: float = Form(..., ge=-90, le=90),
    longitude: float = Form(..., ge=-180, le=180),
    image: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> AnswerResult:
    """Check a photo and the player's location against a clue's target."""
    image_bytes = image.file.read(MAX_IMAGE_BYTES + 1)
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Image too large")
    try:
        result = verify_answer(session, clue_id, image_bytes, latitude, longitude)
    except ClueNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except ValueError as exc:  # raised by ocr_service._decode for unreadable images
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    return AnswerResult(correct=result.correct, message=result.message)