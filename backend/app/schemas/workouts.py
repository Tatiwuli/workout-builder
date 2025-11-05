from typing import Dict, List, Optional, Any
from pydantic import BaseModel


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


class ProgressPayload(BaseModel):
    progress: int
    message: str
    status: str
    final_plan: Optional[Dict[str, Any]] = None


