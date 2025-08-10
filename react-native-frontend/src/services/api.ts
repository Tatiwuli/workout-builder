import {
  ProcessedResponses,
  WorkoutPlan,
  ApiUserResponses,
  WorkoutGenerationResponse,
} from "../types"
import { Platform } from "react-native"

// Configuration interface for API settings
interface ApiConfig {
  baseUrl: string
  retryCount: number
  retryDelay: number
  timeout: number
}

// Default configuration with fallbacks
const getDefaultConfig = (): ApiConfig => {
  // Try to use environment variables first, fall back to sensible defaults
  const baseUrl = (() => {
    // Check for environment variables (requires correct bundler support)
    if (typeof process !== "undefined" && process.env) {
      const env = process.env as unknown as Record<string, string | undefined>
      const expoPublic = env["EXPO_PUBLIC_API_URL"]
      if (expoPublic) {
        return expoPublic
      }
      const reactApp = env["REACT_APP_API_URL"]
      if (reactApp) {
        return reactApp
      }
      const apiUrl = env["API_URL"]
      if (apiUrl) {
        return apiUrl
      }
    }

    // Fallback to platform-specific defaults for development
    return Platform.OS === "web"
      ? "http://localhost:8000"
      : "http://10.0.2.2:8000" // Android emulator
  })()

  const env =
    typeof process !== "undefined" && process.env
      ? (process.env as unknown as Record<string, string | undefined>)
      : {}

  return {
    baseUrl,
    retryCount: Number(env["API_RETRY_COUNT"]) || 2,
    retryDelay: Number(env["API_RETRY_DELAY"]) || 2000,
    timeout: Number(env["API_TIMEOUT"]) || 30000,
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

    try {
      const url = `${this.config.baseUrl}${endpoint}`
      console.log(`API Request: ${url} (${retriesLeft + 1} attempts remaining)`)

      const response = await fetch(url, {
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        ...options,
      })

      // If server responds with error status, throw an error to be handled by catch
      if (!response.ok) {
        const errorText = await response.text()
        throw new ApiError(
          `HTTP ${response.status}: ${errorText || response.statusText}`,
          response.status
        )
      }

      // Success case - return data directly
      const data = await response.json()
      console.log(`API Request succeeded: ${url}`)
      return data
    } catch (error) {
      // Decide which errors are worth retrying
      const shouldRetry =
        (error instanceof ApiError && error.status >= 500) || // 5xx server errors
        !(error instanceof ApiError) // Network/client-side errors

      // If we can retry and have attempts left
      if (shouldRetry && retriesLeft > 0) {
        console.warn(`Request failed, retrying... ${retriesLeft} attempts left`)
        await this.delay(this.config.retryDelay)
        return this.request(endpoint, options, retriesLeft - 1)
      }

      // If we can't retry or are out of attempts, throw the error
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error"
      console.error(`All retry attempts failed: ${errorMessage}`)
      throw new Error(errorMessage)
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms))
  }

  /**
   * Generate workout plan based on user responses
   * Returns either a complete WorkoutPlan or a session_id for polling
   * Throws error on failure - wrap in try/catch when calling
   */
  async generateWorkoutPlan(
    responses: ApiUserResponses
  ): Promise<WorkoutGenerationResponse> {
    const response = await this.request<any>("/generate_workout_plan", {
      method: "POST",
      body: JSON.stringify(responses),
    })

    // Backend returns { success: true, session_id: ... } format
    // Transform to match our expected interface
    console.log("generateWorkoutPlan raw response:", response)
    console.log("response.success:", response.success)
    console.log("response.session_id:", response.session_id)

    if (response.success && response.session_id) {
      console.log("Returning extracted session_id:", response.session_id)
      return { session_id: response.session_id }
    } else if (response.session_id) {
      console.log(
        "Returning session_id (no success field):",
        response.session_id
      )
      return { session_id: response.session_id }
    } else {
      console.log("Returning full response as fallback")
      // Fallback - return response directly if no wrapper
      return response
    }
  }

  /**
   * Get available muscle groups
   * Throws error on failure - wrap in try/catch when calling
   */
  async getMuscleGroups(): Promise<string[]> {
    return this.request<string[]>("/muscle_groups")
  }

  /**
   * Get questionnaire options
   * Throws error on failure - wrap in try/catch when calling
   */
  async getQuestionnaireOptions(): Promise<Record<string, string[]>> {
    return this.request<Record<string, string[]>>("/questionnaire_options")
  }

  /**
   * Save workout plan
   * Throws error on failure - wrap in try/catch when calling
   */
  async saveWorkoutPlan(workoutPlan: WorkoutPlan): Promise<{ id: string }> {
    return this.request<{ id: string }>("/save_workout_plan", {
      method: "POST",
      body: JSON.stringify(workoutPlan),
    })
  }

  /**
   * Get saved workout plans
   * Throws error on failure - wrap in try/catch when calling
   */
  async getSavedWorkoutPlans(): Promise<WorkoutPlan[]> {
    return this.request<WorkoutPlan[]>("/saved_workout_plans")
  }

  /**
   * Get generation progress for a session
   * Throws error on failure - wrap in try/catch when calling
   */
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

    // Backend returns { success: true, data: {...} } format
    // Extract the data field for the new async/await pattern
    if (response.success && response.data) {
      console.log("Returning response.data:", response.data)
      return response.data
    } else if (response.data) {
      console.log("Returning response.data (no success field):", response.data)
      return response.data
    } else {
      console.log("Returning full response as fallback:", response)
      // Fallback - return response directly if no wrapper
      return response
    }
  }

  /**
   * Get the final workout plan for a completed session
   * Throws error on failure - wrap in try/catch when calling
   */
  async getFinalPlan(sessionId: string): Promise<WorkoutPlan> {
    const response = await this.request<any>(`/get_final_plan/${sessionId}`)
    // Backend returns { success: true, data: {...} }
    if (response?.success && response?.data) {
      return response.data as WorkoutPlan
    }
    // Fallback to direct plan if already unwrapped
    return response as WorkoutPlan
  }

  /**
   * Test API connection
   * Returns boolean instead of throwing to keep simple interface
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.request<any>("/health")
      return true
    } catch (error) {
      return false
    }
  }
}

export const apiService = new ApiService()

export default ApiService
