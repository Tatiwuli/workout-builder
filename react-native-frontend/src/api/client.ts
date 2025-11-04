import { API_BASE } from "../env"

export interface ApiConfig {
  baseUrl: string
  retryCount: number
  retryDelay: number
  timeout: number
}

class ApiError extends Error {
  constructor(
    message: string,
    public status: number
  ) {
    super(message)
    this.name = "ApiError"
  }
}

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

export class ApiClient {
  private config: ApiConfig

  constructor(config?: Partial<ApiConfig>) {
    const defaultConfig = getDefaultConfig()
    this.config = { ...defaultConfig, ...config }
  }

  updateConfig(newConfig: Partial<ApiConfig>) {
    this.config = { ...this.config, ...newConfig }
  }

  getConfig(): ApiConfig {
    return { ...this.config }
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {},
    retries?: number
  ): Promise<T> {
    const retriesLeft = retries ?? this.config.retryCount

    const base = this.config.baseUrl.replace(/\/+$/, "")
    const path = endpoint.startsWith("/") ? endpoint : `/${endpoint}`
    const url = `${base}${path}`

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout)

    try {
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
      return data
    } catch (error) {
      clearTimeout(timeoutId)

      const shouldRetry =
        (error instanceof ApiError && error.status >= 500) ||
        !(error instanceof ApiError)

      if (shouldRetry && retriesLeft > 0) {
        await new Promise((resolve) =>
          setTimeout(resolve, this.config.retryDelay)
        )
        return this.request(endpoint, options, retriesLeft - 1)
      }

      const errorMessage =
        error instanceof Error ? error.message : "Unknown error"
      throw new Error(errorMessage)
    }
  }
}

export const apiClient = new ApiClient()

export type { ApiError }
