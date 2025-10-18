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

  updateConfig(newConfig: Partial<ApiConfig>) {
    this.config = { ...this.config, ...newConfig }
    console.log("ApiService config updated:", this.config)
  }

  getConfig(): ApiConfig {
    return { ...this.config }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    retries?: number
  ): Promise<T> {
    const retriesLeft = retries ?? this.config.retryCount

    const base = this.config.baseUrl.replace(/\/+$/, "")
    const path = endpoint.startsWith("/") ? endpoint : `/${endpoint}`
    const url = `${base}${path}`

    // config to cancel http request when timeout
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout)

    try {
      console.log(
        `API Request: ${url} (${
          retriesLeft + 1
        } attempts remaining). Still reconnecting to the server`
      )

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
        console.warn(
          `Request failed, retrying... ${retriesLeft} attempts left.Still reconnecting to the server `
        )
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

    if (response.success) {
      return { session_id: response.session_id }
    } else {
      throw new Error(response.error || "Failed to start workout generation")
    }
  }

  async getMuscleGroups(): Promise<string[]> {
    const response = await this.request<any>("/muscle_groups")
    if (response.success) {
      return response.data
    } else {
      throw new Error(response.error || "Failed to fetch muscle groups")
    }
  }

  async getQuestionnaireOptions(): Promise<Record<string, string[]>> {
    const response = await this.request<any>("/questionnaire_options")
    if (response.success) {
      return response.data
    } else {
      throw new Error(response.error || "Failed to fetch questionnaire options")
    }
  }

  async getGenerationProgress(sessionId: string): Promise<ProgressResponse> {
    const response = await this.request<any>(
      `/generation_progress/${sessionId}`
    )

    console.log(
      "getGenerationProgress raw response:",
      JSON.stringify(response, null, 2)
    )

    if (response.success) {
      return response.data
    } else {
      throw new Error(response.error || "Failed to get generation progress")
    }
  }

  async getFinalPlan(sessionId: string): Promise<WorkoutPlan> {
    const response = await this.request<any>(`/get_final_plan/${sessionId}`)
    if (response.success) {
      return response.data as WorkoutPlan
    } else {
      throw new Error(response.error || "Failed to get final plan")
    }
  }

  async testConnection(): Promise<boolean> {
    try {
      const response = await this.request<any>("/health")
      return response.success
    } catch {
      return false
    }
  }
}

export const apiService = new ApiService()

export default ApiService
