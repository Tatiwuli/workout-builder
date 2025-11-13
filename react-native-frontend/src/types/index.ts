export interface MuscleGroup {
  name: string
  selected: boolean
}

export interface UserResponse {
  Frequency?: string
  Duration?: string
  Experience?: string
}

export interface ProcessedResponses {
  frequency: string
  duration: string
  experience: string
  selectedMuscles: string[]
  muscleGoals?: Record<string, string[]>
}

export interface ApiUserResponses {
  muscle_groups: string[]
  frequency: string
  duration: number
  experience: string
  muscle_goals?: Record<string, string[]>
  muscle_frequencies?: Record<string, string>
}

export interface Exercise {
  exercise_name: string
  setup: string
  execution: string | string[]
  media_url?: string
  reps: number

  weight?: number // optional for warmup exercises
  sets?: number // optional for main exercise
  rest_time?: number // Duration in minutes as float
  alternative_exercise?: string
  alternative_exercise_setup?: string
  alternative_exercise_execution?: string | string[]
  alternative_exercise_media_url?: string
  alternative_exercise_reps?: string
  alternative_exercise_weight?: string
  additional_tips?: string
}

export interface WarmupSection {
  warmup_duration: number // Duration in minutes as float
  warmup_exercises: Exercise[]
}

export interface WorkoutSet {
  set_number: number
  set_duration: number // Duration in minutes as float
  num_rounds: number
  set_strategy?: string
  target_muscle_group: string[]
  exercises: Exercise[]
}

export interface WorkoutPlan {
  workout_title: string
  total_workout_duration: number // Duration in minutes as float
  num_exercises: number
  warmup: WarmupSection
  sets: WorkoutSet[]
}

// Response from generateWorkoutPlan API - could be immediate plan or session for polling
export interface WorkoutGenerationResponse extends Partial<WorkoutPlan> {
  session_id?: string
}

export interface QuestionnaireState {
  responses: UserResponse
  processedResponses?: ProcessedResponses
  questionIndex: number
  selectedMuscles: string[]
  workflowStage: "muscle_selection" | "questionnaire"
  isGeneratingPlan: boolean
  planGenerated: boolean
}

export const PULL_OPTIONS = ["Biceps", "Back"]
export const PUSH_OPTIONS = ["Chest", "Shoulders", "Triceps"]
export const LEG_OPTIONS = ["Glutes", "Hamstrings", "Quadriceps", "Calves"]
export const QUESTIONS = ["Frequency", "Duration", "Experience"]

export const MUSCLE_GOAL_OPTIONS: Record<string, string[]> = {
  Back: ["Wider Back", "Thicker Back", "Defined Back"],
  Chest: ["Upper Chest Focus", "Lower Chest Focus", "Overall Chest Growth"],
  Shoulders: ["3D Shoulders", "Strong Shoulders", "Defined Shoulders"],
  Triceps: ["Bigger Triceps", "Defined Triceps", "Pressing Power"],
  Glutes: ["Lifted Glutes", "Fuller Glutes", "Glute Strength"],
  Hamstrings: ["Bigger Hamstrings", "Defined Hamstrings", "Explosive Power"],
  Quadriceps: ["Bigger Quads", "Defined Quads", "Leg Power"],
  Calves: ["Bigger Calves", "Defined Calves", "Functional Strength"],
}
