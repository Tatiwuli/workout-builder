import { ProcessedResponses, WorkoutPlan } from "../types"

const API_BASE_URL = "http://localhost:8000"

export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  session_id?: string
}

export interface ProgressResponse {
  progress: number
  message: string
}

class ApiService {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`
      const response = await fetch(url, {
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        ...options,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return { success: true, data }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      }
    }
  }

  /**
   * Generate workout plan based on user responses
   */
  async generateWorkoutPlan(
    responses: ProcessedResponses
  ): Promise<ApiResponse<WorkoutPlan>> {
    return this.request<WorkoutPlan>("/generate_workout_plan", {
      method: "POST",
      body: JSON.stringify(responses),
    })
  }

  /**
   * Get available muscle groups
   */
  async getMuscleGroups(): Promise<ApiResponse<string[]>> {
    return this.request<string[]>("/muscle_groups")
  }

  /**
   * Get questionnaire options
   */
  async getQuestionnaireOptions(): Promise<
    ApiResponse<Record<string, string[]>>
  > {
    return this.request<Record<string, string[]>>("/questionnaire_options")
  }

  /**
   * Save workout plan
   */
  async saveWorkoutPlan(
    workoutPlan: WorkoutPlan
  ): Promise<ApiResponse<{ id: string }>> {
    return this.request<{ id: string }>("/save_workout_plan", {
      method: "POST",
      body: JSON.stringify(workoutPlan),
    })
  }

  /**
   * Get saved workout plans
   */
  async getSavedWorkoutPlans(): Promise<ApiResponse<WorkoutPlan[]>> {
    return this.request<WorkoutPlan[]>("/saved_workout_plans")
  }

  /**
   * Get generation progress for a session
   */
  async getGenerat