import {
  ProcessedResponses,
  WorkoutPlan,
  ApiUserResponses,
  WorkoutGenerationResponse,
} from "../types"
import { Platform } from "react-native"
import { API_BASE } from "../env" 

// Configuration interface for API settings
interface ApiConfig {
  baseUrl: string
  retryCount: number
  retryDelay: number
  timeout: number
}

// Default configuration with fallbacks
const getDefaultConfig = (): ApiConfig => {
  return {
    baseUrl: API_BASE,
    retryCount:
      Number(
        (process.env as Record<string, string | undefined>).API_RETRY_COUNT
      ) || 5,
    retryDelay:
      Number(
        (process.env as Record<string, string | undefined>).API_RETRY_DELAY
      ) || 5000,
    timeout:
      Number((process.env as Record<string, string | undefined>).API_TIMEOUT) ||
      60000,
  }
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  session_id?: string
}

class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message)
    this.name = "ApiError"
  }
}

export interface ProgressResponse {
  progress: number
  message: string
  status?: string
  final_plan?: any
}

/**
 * API Service with configurable retry functionality
 *
 * Features:
 * - Environment-based configuration (dev/staging/prod)
 * - Configurable retry counts and delays
 * - Automatic retry for network errors and 5xx server errors
 * - No retry for 4xx client errors (user input issues, auth, etc.)
 */
class ApiService {
  private config: ApiConfig

  constructor(config?: Partial<ApiConfig>) {
    const defaultConfig = getDefaultConfig()
    this.config = { ...defaultConfig, ...config }

    console.log("ApiService initialized with config:", {
      baseUrl: this.config.baseUrl,
      retryCount: this.config.retryCount,
      retryDelay: this.config.retryDelay,
      timeout: this.config.timeout,
    })
  }

  // Method to update configuration
  updateConfig(newConfig: Partial<ApiConfig>) {
    this.config = { ...this.config, ...newConfig }
    console.log("ApiService config updated:", this.config)
  }

  // Method to get current configuration
  getConfig(): ApiConfig {
    return { ...this.config }
  }

  // Legacy method for backward compatibility
  setBaseUrl(url: string) {
    this.updateConfig({ baseUrl: url })
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    retries?: number
  ): Promise<T> {
    const retriesLeft = retries ?? this.config.retryCount

    // ✅ Safe URL join
    const base = this.config.baseUrl.replace(/\/+$/, "")
    const path = endpoint.startsWith("/") ? endpoint : `/${endpoint}`
    const url = `${base}${path}`

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout)

    try {
      console.log(`API Request: ${url} (${retriesLeft + 1} attempts remaining). Still reconnecting to the server that runs on a Render free tier`)

      const response = await fetch(url, {
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        signal: controller.signal,
        ...options,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const errorText = await response.text().catch(() => "")
        throw new ApiError(
          `HTTP ${response.status}: ${errorText || response.statusText}`,
          response.status
        )
      }

      const data = await response.json()
      console.log(`API Request succeeded: ${url}`)
      return data
    } catch (error) {
      clearTimeout(timeoutId)

      const shouldRetry =
        (error instanceof ApiError && error.status >= 500) || // 5xx server errors
        !(error instanceof ApiError) // Network/client-side errors

      if (shouldRetry && retriesLeft > 0) {
        console.warn(`Request failed, retrying... ${retriesLeft} attempts left.Still reconnecting to the server that runs on a Render free tier `)
        await this.delay(this.config.retryDelay)
        return this.request(endpoint, options, retriesLeft - 1)
      }

      const errorMessage =
        error instanceof Error ? error.message : "Unknown error"
      console.error(`All retry attempts failed: ${errorMessage}`)
      throw new Error(errorMessage)
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms))
  }

  async generateWorkoutPlan(
    responses: ApiUserResponses
  ): Promise<WorkoutGenerationResponse> {
    const response = await this.request<any>("/generate_workout_plan", {
      method: "POST",
      body: JSON.stringify(responses),
    })

    console.log("generateWorkoutPlan raw response:", response)
    console.log("response.success:", response.success)
    console.log("response.session_id:", response.session_id)

    if (response.success && response.session_id) {
      return { session_id: response.session_id }
    } else if (response.session_id) {
      return { session_id: response.session_id }
    } else {
      return response
    }
  }

  async getMuscleGroups(): Promise<string[]> {
    return this.request<string[]>("/muscle_groups")
  }

  async getQuestionnaireOptions(): Promise<Record<string, string[]>> {
    return this.request<Record<string, string[]>>("/questionnaire_options")
  }

  async saveWorkoutPlan(workoutPlan: WorkoutPlan): Promise<{ id: string }> {
    return this.request<{ id: string }>("/save_workout_plan", {
      method: "POST",
      body: JSON.stringify(workoutPlan),
    })
  }

  async getSavedWorkoutPlans(): Promise<WorkoutPlan[]> {
    return this.request<WorkoutPlan[]>("/saved_workout_plans")
  }

  async getGenerationProgress(sessionId: string): Promise<ProgressResponse> {
    const response = await this.request<any>(
      `/generation_progress/${sessionId}`
    )

    console.log(
      "getGenerationProgress raw response:",
      JSON.stringify(response, null, 2)
    )
    console.log("response.success:", response.success)
    console.log("response.data:", response.data)

    if (response.success && response.data) {
      return response.data
    } else if (response.data) {
      return response.data
    } else {
      return response
    }
  }

  async getFinalPlan(sessionId: string): Promise<WorkoutPlan> {
    const response = await this.request<any>(`/get_final_plan/${sessionId}`)
    if (response?.success && response?.data) {
      return response.data as WorkoutPlan
    }
    return response as WorkoutPlan
  }

  async testConnection(): Promise<boolean> {
    try {
      await this.request<any>("/health")
      return true
    } catch {
      return false
    }
  }
}

export const apiService = new ApiService()

export default ApiService
