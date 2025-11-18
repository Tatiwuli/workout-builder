from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel


class UserResponses(BaseModel):
    muscle_groups: List[str]
    frequency: str
    duration: int
    experience: str
    muscle_goals: Optional[Dict[str, List[str]]] = {}
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


# Exercise Selector Agent Models

class TargetMusclePart(BaseModel):
    muscle_group: str
    muscle_part: List[str]

class SelectedExercise(BaseModel):
    exercise_name: str
    setup: List[str]
    execution: List[str]
    
    media_url: str
    target_muscles: List[str]
    target_muscle_parts: List[TargetMusclePart]
    additional_notes: str
    alternative_exercise: str
    alternative_exercise_setup: List[str]
    alternative_exercise_execution: List[str]
    alternative_exercise_media_url:str
    selection_reason: str
    



class ExerciseSelectorOutput(BaseModel):
    exercises: List[SelectedExercise]


# Workout Planner Agent Models

class PlannedExercise(BaseModel):
    exercise_name: str
    reps: str
    weight: str
    alternative_exercise: str
    alternative_exercise_reps: str
    alternative_exercise_weight: str


class PlannedSet(BaseModel):
    set_number: int
    set_duration: float
    set_strategy: str
    set_rest_time: float 
    num_rounds: int
    target_muscle_group: List[str]
    set_reasoning: str
    exercises: List[PlannedExercise]


class WorkoutPlannerOutput(BaseModel):
    sets: List[PlannedSet]
    workout_explanation: str



class ExerciseFinal(BaseModel):
    exercise_name: str
    target_muscle_part: List[TargetMusclePart]
    setup: List[str]
    execution: List[str]
    media_url: str
    reps: str
    weight: str
    alternative_exercise: str
    alternative_exercise_setup: List[str]
    alternative_exercise_execution: List[str]
    alternative_exercise_media_url: str
    alternative_exercise_reps: str
    alternative_exercise_weight: str
    additional_tips: str


class WorkoutSetFinal(BaseModel):
    set_number: int
    set_strategy: str
    set_duration: float
    set_rest_time: float 
    num_rounds: int
    target_muscle_group: List[str]
    exercises: List[ExerciseFinal]


class WorkoutPlanWithoutWarmup(BaseModel):
    workout_title: str
    total_workout_duration: float
    num_exercises: int
    sets: List[WorkoutSetFinal]


#Warmup Agent Models

class WarmupExerciseFinal(BaseModel):
    exercise_name: str
    sets_reps: str 
    setup: List[str]
    execution: List[str]
    duration: float


class WarmupSectionFinal(BaseModel):
    total_warmup_duration: float
    warmup_exercises: List[WarmupExerciseFinal]

class FinalWorkoutPlan(BaseModel):
    workout_title: str
    total_workout_duration: float
    num_exercises: int
    warmup: WarmupSectionFinal
    sets: List[WorkoutSetFinal]



