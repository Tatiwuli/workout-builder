"""
FastAPI server to expose workout builder functionality as REST API
for React Native frontend integration
"""

from datetime import datetime
import threading
import asyncio
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import sys
import os

from frontend.utils import process_user_responses
from agents.build_workout_plan import WorkoutBuilderWorkflow
# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


app = FastAPI(title="Workout Builder API", version="1.0.0")
raw_origins = os.getenv("CORS_ORIGINS", "")
ALLOWED_ORIGINS = [o.strip() for o in raw_origins.split(",") if o.strip()]
# Enable CORS for React Native
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models


class UserResponses(BaseModel):
    muscle_groups: List[str]
    goal: str
    frequency: str
    duration: int
    experience: str
    muscle_goals: Optional[Dict[str, str]] = {}
    muscle_frequencies: Optional[Dict[str, str]] = {}


class WorkoutPlanResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    progress: Optional[int] = None


class MuscleGroup(BaseModel):
    name: str
    category: str  # "push", "pull", "legs"


# Global storage for progress tracking (in production, use Redis/DB)
generation_progress = {}

# API Endpoints


@app.get("/")
async def root():
    return {
        "success": True,
        "data": {"message": "Workout Builder API is running", "version": "1.0.0"}
    }


@app.get("/health")
async def health_check():
    return {
        "success": True,
        "data": {"status": "healthy", "timestamp": datetime.now().isoformat()}
    }


@app.get("/muscle_groups")
async def get_muscle_groups():
    """Get available muscle groups for selection"""
    muscle_groups = {
        "push": ["Chest", "Shoulders", "Triceps"],
        "pull": ["Biceps", "Back"],
        "legs": ["Glutes", "Hamstrings", "Quadriceps", "Calves"]
    }
    return {"success": True, "data": muscle_groups}


@app.get("/questionnaire_options")
async def get_questionnaire_options():
    """Get available options for questionnaire dropdowns"""
    options = {
        "goals": [
            "Build muscle (hypertrophy)",
            "Increase strength",
            "Improve endurance",
            "Lose weight",
            "General fitness"
        ],
        "frequency": [
            "1-2 times per week",
            "3-4 times per week",
            "5-6 times per week",
            "Daily"
        ],
        "experience": [
            "I'm just starting out and have less than 3 months of experience.",
            "I've been consistently training for 3 months to 1 year.",
            "I've been training regularly for 1 to 2 years",
            "I've been training regularly for 2 to 3 years"
        ]
    }
    return {"success": True, "data": options}


@app.post("/generate_workout_plan")
async def generate_workout_plan(user_data: UserResponses):
    """Start generating a personalized workout plan using AI agents"""
    try:
        # Generate unique session ID for progress tracking
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        generation_progress[session_id] = {
            "progress": 0,
            "message": "Starting workout generation...",
            "status": "running",
            "final_plan": None
        }

        # Start the generation in a background task

        def run_generation():
            try:
                print(f"Starting generation for session {session_id}")

                # Convert user responses to the format expected by the workflow
                raw_responses = {
                    "muscle_groups": user_data.muscle_groups,
                    "goal": user_data.goal,
                    "frequency": user_data.frequency,
                    "workout_duration": user_data.duration,
                    "experience_level_description": user_data.experience,
                    **user_data.muscle_goals,
                    **user_data.muscle_frequencies
                }

                print(f"Raw responses: {raw_responses}")

                
                processed_responses = process_user_responses(raw_responses)
                print(f"Processed responses: {processed_responses}")

             
                def progress_callback(message: str, percentage: int):
                    print(f"Progress update: {percentage}% - {message}")
                    generation_progress[session_id] = {
                        "progress": percentage,
                        "message": message,
                        "status": "running",
                        "final_plan": generation_progress[session_id].get("final_plan")
                    }

                # Check for required environment variables and use mock if missing
                import os
                use_mock = False
                if not os.getenv("OPENAI_API_KEY") or not os.getenv("GEMINI_API_KEY") or not os.getenv("MONGODB_URI"):
                    print("Missing environment variables, using mock workflow...")
                    use_mock = True

                if use_mock:
                    # Mock workflow for development
                    import time

                    progress_callback(
                        "Starting mock workout generation...", 10)
                    time.sleep(1)

                    progress_callback("Selecting exercises...", 30)
                    time.sleep(1)

                    progress_callback("Structuring workout...", 60)
                    time.sleep(1)

                    progress_callback("Finalizing plan...", 90)
                    time.sleep(1)

                    # Create a mock workout plan
                    final_plan = {
                        "workout_title": "Your Personalized Workout Plan (Mock)",
                        "workout_description": f"A {processed_responses.get('frequency', '3-4 times per week')} workout plan focused on {', '.join(processed_responses.get('muscle_groups', ['general fitness']))}.",
                        "workout_duration": processed_responses.get('workout_duration', 45),
                        "experience_level": processed_responses.get('experience_level_description', 'intermediate'),
                        "days": [
                            {
                                "day": "Day 1",
                                "focus": "Upper Body",
                                "exercises": [
                                    {
                                        "name": "Push-ups",
                                        "sets": 3,
                                        "reps": "8-12",
                                        "rest": "60 seconds",
                                        "instructions": "Keep your body in a straight line from head to heels."
                                    },
                                    {
                                        "name": "Pull-ups",
                                        "sets": 3,
                                        "reps": "5-8",
                                        "rest": "90 seconds",
                                        "instructions": "Use assisted variations if needed."
                                    }
                                ]
                            }
                        ],
                        "notes": "This is a demo workout plan. For a real personalized plan, configure the environment variables.",
                        "is_mock": True
                    }
                else:
                    # Initialize workflow
                    print("Initializing workflow...")
                    workflow = WorkoutBuilderWorkflow(
                        progress_callback=progress_callback)

                    # Generate workout plan using existing AI agents
                    print("Running workflow...")
                    final_plan = workflow.run_workflow(processed_responses)

                print("Workflow completed successfully!")
                # Update progress to complete with final plan
                generation_progress[session_id] = {
                    "progress": 100,
                    "message": "Workout plan generated successfully! 🎉",
                    "status": "completed",
                    "final_plan": final_plan
                }

            except Exception as e:
                print(f"Error in generation: {str(e)}")
                import traceback
                traceback.print_exc()
                generation_progress[session_id] = {
                    "progress": 0,
                    "message": f"Error: {str(e)}",
                    "status": "error",
                    "final_plan": None
                }

        # Start generation in background thread
        thread = threading.Thread(target=run_generation)
        thread.daemon = True
        thread.start()

        return {
            "success": True,
            "data": {"message": "Generation started. Use /generation_progress/{session_id} to track progress."},
            "session_id": session_id
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to start workout plan generation: {str(e)}"
        }


@app.get("/generation_progress/{session_id}")
async def get_generation_progress(session_id: str):
    """Get progress of workout plan generation"""
    print(f"Progress request for session: {session_id}")
    print(f"Available sessions: {list(generation_progress.keys())}")

    if session_id in generation_progress:
        progress_data = generation_progress[session_id]
        print(f"Progress data: {progress_data}")
        return {
            "success": True,
            "data": {
                "progress": progress_data["progress"],
                "message": progress_data["message"],
                "status": progress_data["status"],
                "final_plan": progress_data.get("final_plan")
            }
        }
    else:
        print(f"Session {session_id} not found in generation_progress")
        return {
            "success": False,
            "error": "Session not found"
        }


@app.get("/get_final_plan/{session_id}")
async def get_final_plan(session_id: str):
    """Get the final workout plan for a completed session"""
    if session_id in generation_progress:
        progress_data = generation_progress[session_id]
        if progress_data["status"] == "completed" and progress_data.get("final_plan"):
            return {
                "success": True,
                "data": progress_data["final_plan"]
            }
        else:
            return {
                "success": False,
                "error": "Workout plan not ready or not found"
            }
    else:
        return {
            "success": False,
            "error": "Session not found"
        }


if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
