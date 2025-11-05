from datetime import datetime
import threading
from typing import Dict, Any, Callable

from backend.agents.build_workout_plan import WorkoutBuilderWorkflow
from .user_response_processor import process_user_responses


# Simple in-memory progress store
generation_progress: Dict[str, Dict[str, Any]] = {}


def start_generation(user_data: Dict[str, Any]) -> str:
    """Start background generation and return a session_id."""
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    generation_progress[session_id] = {
        "progress": 0,
        "message": "Starting workout generation...",
        "status": "running",
        "final_plan": None,
    }

    def run_generation() -> None:
        try:
            raw_responses = {
                "muscle_groups": user_data["muscle_groups"],
                "goal": user_data["goal"],
                "frequency": user_data["frequency"],
                "workout_duration": user_data["duration"],
                "experience_level_description": user_data["experience"],
                **(user_data.get("muscle_goals") or {}),
                **(user_data.get("muscle_frequencies") or {}),
            }

            processed_responses = process_user_responses(raw_responses)

            def progress_callback(message: str, percentage: int) -> None:
                generation_progress[session_id] = {
                    "progress": percentage,
                    "message": message,
                    "status": "running",
                    "final_plan": generation_progress[session_id].get("final_plan"),
                }

            workflow = WorkoutBuilderWorkflow(progress_callback=progress_callback)
            final_plan = workflow.run_workflow(processed_responses)

            generation_progress[session_id] = {
                "progress": 100,
                "message": "Workout plan generated successfully! 🎉",
                "status": "completed",
                "final_plan": final_plan,
            }
        except Exception as e:  # noqa: BLE001
            generation_progress[session_id] = {
                "progress": 0,
                "message": f"Error: {str(e)}",
                "status": "error",
                "final_plan": None,
            }

    thread = threading.Thread(target=run_generation, daemon=True)
    thread.start()
    return session_id


def get_progress(session_id: str) -> Dict[str, Any] | None:
    return generation_progress.get(session_id)


