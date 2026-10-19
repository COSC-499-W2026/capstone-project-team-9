from pathlib import Path

import cv2
import numpy as np
import pytest
from services import ocr_service
from services.ocr_service import _extract_codes, matches_room, read_room_codes

# Adjust to wherever your preset photos live. Files are named by room code, e.g. COM301.jpeg
SUBMISSIONS_DIR = Path(__file__).parent / "db" / "submissions"


@pytest.fixture
def image_bytes():
    """A valid (blank) JPEG so decoding works; OCR itself is faked in unit tests."""
    ok, buf = cv2.imencode(".jpg", np.zeros((100, 200, 3), dtype=np.uint8))
    return buf.tobytes()


@pytest.fixture
def fake_ocr(monkeypatch):
    """Make each OCR pass return the next string in the list."""
    def install(*texts):
        results = iter(texts)
        monkeypatch.setattr(ocr_service, "_ocr_text", lambda image: next(results))
    return install


@pytest.mark.parametrize("text,expected", [
    ("COM301", ["COM301"]),
    ("COM 301", ["COM301"]),
    ("EME0050", ["EME0050"]),
    ("C0M3O1", ["COM301"]),          # zero/O confusion
    ("LIB3I4", ["LIB314"]),          # I read for 1
    ("EXIT ROOM COM301 STAIRS", ["COM301"]),
])
def test_extract_codes_finds_and_corrects(text, expected):
    assert expected[0] in _extract_codes(text)


@pytest.mark.parametrize("text", ["", "EXIT", "12345", "HELLO WORLD"])
def test_extract_codes_ignores_non_codes(text):
    assert _extract_codes(text) == []


def test_matches_room_true_when_code_present(image_bytes, fake_ocr):
    fake_ocr("COM301")
    assert matches_room(image_bytes, "COM301") is True


def test_matches_room_is_case_insensitive_on_expected(image_bytes, fake_ocr):
    fake_ocr("COM301")
    assert matches_room(image_bytes, "com301") is True


def test_matches_room_false_for_wrong_room(image_bytes, fake_ocr):
    fake_ocr("LIB314", "LIB314")
    assert matches_room(image_bytes, "COM301") is False


def test_second_pass_rescues_a_failed_first_pass(image_bytes, fake_ocr):
    fake_ocr("", "COM301")
    assert matches_room(image_bytes, "COM301") is True


def test_second_pass_not_run_when_first_matches(image_bytes, fake_ocr):
    fake_ocr("COM301")  # a second call would raise StopIteration
    assert matches_room(image_bytes, "COM301") is True


def test_read_room_codes_dedupes_across_passes(image_bytes, fake_ocr):
    fake_ocr("COM301", "COM301")
    assert read_room_codes(image_bytes) == ["COM301"]


def test_unreadable_bytes_raise_value_error():
    with pytest.raises(ValueError):
        matches_room(b"not an image", "COM301")


# Real-photo check: runs actual EasyOCR on your preset submissions.
@pytest.mark.skipif(not SUBMISSIONS_DIR.exists(), reason="no sample photos in repo")
@pytest.mark.parametrize("photo", sorted(SUBMISSIONS_DIR.glob("*.jp*g")), ids=lambda p: p.stem)
def test_real_submission_matches_its_own_room(photo):
    assert matches_room(photo.read_bytes(), photo.stem) is True