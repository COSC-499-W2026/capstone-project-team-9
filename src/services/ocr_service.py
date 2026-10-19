import re
from functools import lru_cache

import cv2
import easyocr
import numpy as np

MAX_LONG_SIDE_PX = 1600
FAR_MAX_LONG_SIDE_PX = 2560  # EasyOCR's own default canvas size
FAR_OPTIONS = {"min_size": 10}  # keep small text boxes; the image is already upscaled
ALLOWLIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
ROOM_CODE_PATTERN = re.compile(r"[A-Z]{3}\d{3,4}")  # COM301, EME0050
CODE_LENGTHS = (6, 7)
MAX_UPSCALE = 1  # don't blow tiny images up more than this

# Common OCR confusions, applied by position (first 3 chars are letters, the rest digits)
TO_LETTER = str.maketrans("012568", "OIZSGB")
TO_DIGIT = str.maketrans("OQDILZSGB", "000112568")


@lru_cache(maxsize=1)
def _get_reader() -> easyocr.Reader:
    """Load the model once; it is slow to construct."""
    return easyocr.Reader(["en"], gpu=False)


def _decode(image_bytes: bytes) -> np.ndarray:
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Not a readable image")
    return image


def _resize_to(image: np.ndarray, target_side: int) -> np.ndarray:
    """Scale so the long side is target_side: shrink big photos (fast OCR), enlarge tiny ones (readable text)."""
    scale = min(target_side / max(image.shape[:2]), MAX_UPSCALE)
    if scale == 1:
        return image
    interpolation = cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC
    return cv2.resize(image, None, fx=scale, fy=scale, interpolation=interpolation)


def _enhance(image: np.ndarray) -> np.ndarray:
    """Grayscale + local contrast boost, for glare and dim hallway lighting."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)


def _ocr_text(image: np.ndarray, **options) -> str:
    pieces = _get_reader().readtext(image, allowlist=ALLOWLIST, detail=0, **options)
    return " ".join(pieces)


def _extract_codes(text: str) -> list[str]:
    """Find room-code-shaped strings, correcting letter/digit confusions by position."""
    squashed = re.sub(r"[^A-Z0-9]", "", text.upper())
    codes = []
    for length in CODE_LENGTHS:
        for i in range(len(squashed) - length + 1):
            window = squashed[i : i + length]
            fixed = window[:3].translate(TO_LETTER) + window[3:].translate(TO_DIGIT)
            if ROOM_CODE_PATTERN.fullmatch(fixed):
                codes.append(fixed)
    return codes


def _codes_per_pass(image_bytes: bytes):
    """Yield the codes found by each OCR pass. Lazy, so later passes only run if needed."""
    original = _decode(image_bytes)
    image = _resize_to(original, MAX_LONG_SIDE_PX)
    yield _extract_codes(_ocr_text(image))
    yield _extract_codes(_ocr_text(_enhance(image)))
    far = _enhance(_resize_to(original, FAR_MAX_LONG_SIDE_PX))
    yield _extract_codes(_ocr_text(far, **FAR_OPTIONS))

def read_room_codes(image_bytes: bytes) -> list[str]:
    """Every room code found in the photo (for debugging and tuning)."""
    found = (code for codes in _codes_per_pass(image_bytes) for code in codes)
    return list(dict.fromkeys(found))


def matches_room(image_bytes: bytes, expected_code: str) -> bool:
    """True if the photo contains the expected room code."""
    expected = expected_code.upper()
    return any(expected in codes for codes in _codes_per_pass(image_bytes))