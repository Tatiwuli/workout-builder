import { apiClient } from "../client"
import { ApiResponse } from "../types"

export async function testConnection(): Promise<boolean> {
  try {
    const response = await apiClient.request<ApiResponse<unknown>>("/health")
    return !!response.success
  } catch {
    return false
  }
}
