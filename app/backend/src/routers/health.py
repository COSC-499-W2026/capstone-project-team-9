from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
def health_check():
    """Confirm the API is running"""
    return {"status": "ok"}