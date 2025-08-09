import { ProcessedResponses, WorkoutPlan, ApiUserResponses } from "../types"
import { Platform } from "react-native"

// Use different URLs for different environments
const API_BASE_URL =
  Platform.OS === "web" ? "http://localhost:8000" : "http://10.0.2.2:8000" // Android emulator uses 10.0.2.2 for localhost

export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  session_id?: string
}

export interface ProgressResponse {
  progress: number
  message: string
  status?: string
  final_plan?: any
}

class ApiService {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  // Method to update base URL for different environments
  setBaseUrl(url: string) {
    this.baseUrl = url
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
    responses: ApiUserResponses
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
  async getGenerationProgress(
    sessionId: string
  ): Promise<ApiResponse<ProgressResponse>> {
    return this.request<ProgressResponse>(`/generation_progress/${sessionId}`)
  }

  /**
   * Get the final workout plan for a completed session
   */
  async getFinalPlan(sessionId: string): Promise<ApiResponse<WorkoutPlan>> {
    return this.request<WorkoutPlan>(`/get_final_plan/${sessionId}`)
  }

  /**
   * Test API connection and find the correct base URL
   */
  async testConnection(): Promise<boolean> {
    try {
      const response = await this.request<any>("/health")
      return response.success
    } catch (error) {
      return false
    }
  }
}

export const apiService = new ApiService()

export default ApiService
