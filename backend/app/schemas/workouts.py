from typing import Dict, List, Optional, Any, Union
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


# Exercise Selector Agent Models
class WarmupExercise(BaseModel):
    exercise_name: str
    setup: str
    execution: str
    sets_reps: str  # String format for warmup exercises
    duration: float


class WarmupSection(BaseModel):
    total_warmup_duration: float
    warmup_exercises: List[WarmupExercise]


class SelectedExercise(BaseModel):
    exercise_name: str
    setup: str
    execution: str
    media_url: str
    alternative_equipment: str
    tier_reasons: str
    targeted_muscles: List[str]
    targeted_muscle_parts: str
    limitations: str
    scientific_insights: str
    additional_notes: str
    alternative_exercise: str
    alternative_exercise_media_url: str
    selection_reason: str


class ExerciseSelectorOutput(BaseModel):
    exercises: List[SelectedExercise]
    warmup: WarmupSection


# Workout Planner Agent Models
class PlannedExercise(BaseModel):
    exercise_name: str
    target_muscle_part: List[Dict[str, List[str]]]
    reps: str
    weight: str
    rest_time: float
    alternative_exercise: str
    alternative_exercise_reps: str
    alternative_exercise_weight: str


class PlannedSet(BaseModel):
    set_number: int
    set_duration: float
    set_strategy: str
    num_rounds: int
    target_muscle_group: List[str]
    set_reasoning: str
    exercises: List[PlannedExercise]


class WorkoutPlannerOutput(BaseModel):
    sets: List[PlannedSet]
    workout_explanation: str


# Personal Trainer Agent Models
class WarmupExerciseFinal(BaseModel):
    exercise_name: str
    reps: int
    sets_reps: Optional[str] = None  # String format for sets and reps description (from exercise selector)
    setup: str
    execution: str


class WarmupSectionFinal(BaseModel):
    warmup_duration: float
    warmup_exercises: List[WarmupExerciseFinal]


class ExerciseFinal(BaseModel):
    exercise_name: str
    target_muscle_part: List[Dict[str, List[str]]]
    setup: str
    execution: Union[str, List[str]]
    media_url: str
    reps: str
    weight: str
    alternative_equipments: str
    rest_time: float
    alternative_exercise: str
    alternative_exercise_setup: str
    alternative_exercise_execution: str
    alternative_exercise_media_url: str
    alternative_exercise_reps: str
    alternative_exercise_weight: str
    additional_tips: str


class WorkoutSetFinal(BaseModel):
    set_number: int
    set_strategy: str
    set_duration: float
    num_rounds: int
    target_muscle_group: List[str]
    exercises: List[ExerciseFinal]


class FinalWorkoutPlan(BaseModel):
    workout_title: str
    total_workout_duration: float
    num_exercises: int
    warmup: WarmupSectionFinal
    sets: List[WorkoutSetFinal]


