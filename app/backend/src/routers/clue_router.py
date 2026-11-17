from fastapi import APIRouter, HTTPException, Response, status

from core.dependencies import ClueRepositoryDep

AUDIO_MEDIA_TYPE = "audio/mpeg"  # clue audio is stored as mp3

router = APIRouter(prefix="/clues", tags=["clues"])


@router.get("/{clue_id}/audio", responses={200: {"content": {AUDIO_MEDIA_TYPE: {}}}})
def get_clue_audio(clue_id: int, clue_repo: ClueRepositoryDep) -> Response:
    """The clue's audio as an mp3. 404 if the clue doesn't exist or has no audio."""
    audio = clue_repo.get_audio(clue_id)
    if audio is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Clue has no audio")
    return Response(content=audio, media_type=AUDIO_MEDIA_TYPE)