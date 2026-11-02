from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlmodel import Session

from core.db import get_session
from services.answer_service import ClueNotFoundError, AnswerResult, verify_answer

MAX_IMAGE_BYTES = 10 * 1024 * 1024

router = APIRouter(prefix="/answers", tags=["answers"])