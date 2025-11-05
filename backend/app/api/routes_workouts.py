from fastapi import APIRouter
from typing import Any, Dict

from backend.app.schemas.workouts import UserResponses
from backend.app.services.workout_generation import start_generation, get_progress

router = APIRouter()


@router.post("/generate_workout_plan")
async def generate_workout_plan(user_data: UserResponses) -> Dict[str, Any]:
    try:
        session_id = start_generation(user_data.model_dump())
        return {
            "success": True,
            "data": {
                "message": "Generation started. Use /generation_progress/{session_id} to track progress.",
            },
            "session_id": session_id,
        }
    except Exception as e:  # noqa: BLE001
        return {
            "success": False,
            "error": f"Failed to start workout plan generation: {str(e)}",
        }


@router.get("/generation_progress/{session_id}")
async def generation_progress(session_id: str) -> Dict[str, Any]:
    progress_data = get_progress(session_id)
    if progress_data is None:
        return {"success": False, "error": "Session not found"}
    return {
        "success": True,
        "data": {
            "progress": progress_data.get("progress"),
            "message": progress_data.get("message"),
            "status": progress_data.get("status"),
            "final_plan": progress_data.get("final_plan"),
        },
    }


@router.get("/get_final_plan/{session_id}")
async def get_final_plan(session_id: str) -> Dict[str, Any]:
    progress_data = get_progress(session_id)
    if progress_data is None:
        return {"success": False, "error": "Session not found"}
    if progress_data.get("status") == "completed" and progress_data.get("final_plan"):
        return {"success": True, "data": progress_data.get("final_plan")}
    return {"success": False, "error": "Workout plan not ready or not found"}


