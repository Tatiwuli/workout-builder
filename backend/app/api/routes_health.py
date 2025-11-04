from datetime import datetime
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {
        "success": True,
        "data": {"message": "Workout Builder API is running", "version": "1.0.0"},
    }


@router.get("/health")
async def health_check():
    return {
        "success": True,
        "data": {"status": "healthy", "timestamp": datetime.now().isoformat()},
    }


