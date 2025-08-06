export interface MuscleGroup {
  name: string;
  selected: boolean;
}

export interface UserResponse {
  Goal?: string;
  Frequency?: string;
  Duration?: string;
  Experience?: string;
}

export interface ProcessedResponses {
  goal: string;
  frequency: string;
  duration: string;
  experience: string;
  selectedMuscles: string[];
}

export interface Exercise {
  exercise_name: string;
  setup_notes: string;
  execution_notes: string;
  media_url?: string;
}

export interface WarmupSection {
  warmup_duration: string;
  warmup_exercises: Exercise[];
}

export interface WorkoutSet {
  set_number: number;
  target_muscle_group: string[];
  exercises: Exercise[];
}

export interface WorkoutPlan {
  workout_title: string;
  total_workout_duration: string;
  num_exercises: number;
  warmup: WarmupSection;
  sets: WorkoutSet[];
}

export interface QuestionnaireState {
  responses: UserResponse;
  processedResponses?: ProcessedResponses;
  questionIndex: number;
  selectedMuscles: string[];
  workflowStage: 'muscle_selection' | 'questionnaire';
  isGeneratingPlan: boolean;
  planGenerated: boolean;
}

export const PULL_OPTIONS = ['Biceps', 'Back'];
export const PUSH_OPTIONS = ['Chest', 'Shoulders', 'Triceps'];
export const LEG_OPTIONS = ['Glutes', 'Hamstrings', 'Quadriceps', 'Calves'];
export const QUESTIONS = ['Goal', 'Frequency', 'Duration', 'Experience']; 