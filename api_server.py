"""
FastAPI server to expose workout builder functionality as REST API
for React Native frontend integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from agents.build_workout_plan import WorkoutBuilderWorkflow
from frontend.utils import process_user_responses
import json
import asyncio
from datetime import datetime

app = FastAPI(title="Workout Builder API", version="1.0.0")

# Enable CORS for React Native
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
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
    return {"message": "Workout Builder API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

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
    """Generate a personalized workout plan using AI agents"""
    try:
        # Generate unique session ID for progress tracking
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        generation_progress[session_id] = {"progress": 0, "message": "Starting..."}
        
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
        
        # Process responses using existing utility
        processed_responses = process_user_responses(raw_responses)
        
        # Progress callback function
        def progress_callback(message: str, percentage: int):
            generation_progress[session_id] = {
                "progress": percentage,
                "message": message
            }
        
        # Initialize workflow
        workflow = WorkoutBuilderWorkflow(progress_callback=progress_callback)
        
        # Generate workout plan using existing AI agents
        final_plan = workflow.run_workflow(processed_responses)
        
        # Update progress to complete
        generation_progress[session_id] = {
            "progress": 100,
            "message": "Workout plan generated successfully!"
        }
        
        return {
            "success": True,
            "data": final_plan,
            "session_id": session_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate workout plan: {str(e)}"
        }

@app.get("/generation_progress/{session_id}")
async def get_generation_progress(session_id: str):
    """Get progress of workout plan generation"""
    if session_id in generation_progress:
        return {
            "success": True,
            "data": generation_progress[session_id]
        }
    else:
        return {
            "success": False,
            "error": "Session not found"
        }

@app.post("/save_workout_plan")
async def save_workout_plan(workout_plan: Dict[str, Any]):
    """Save a generated workout plan"""
    try:
        # In a real implementation, save to database
        # For now, save to JSON file like the current system
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"database/final_workout_plan_json/final_workout_plan_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(workout_plan, f, indent=2)
        
        return {
            "success": True,
            "data": {"id": timestamp, "filename": filename}
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to save workout plan: {str(e)}"
        }

@app.get("/saved_workout_plans")
async def get_saved_workout_plans():
    """Get list of saved workout plans"""
    try:
        plans_dir = "database/final_workout_plan_json/"
        if not os.path.exists(plans_dir):
            return {"success": True, "data": []}
        
        plans = []
        for filename in os.listdir(plans_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(plans_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        plan = json.load(f)
                        plans.append({
                            "id": filename.replace('.json', ''),
                            "filename": filename,
                            "title": plan.get("workout_title", "Untitled Workout"),
                            "created_at": filename.split('_')[-1].replace('.json', '')
                        })
                except Exception:
                    continue
        
        # Sort by creation date (newest first)
        plans.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {"success": True, "data": plans}
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to retrieve saved plans: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)