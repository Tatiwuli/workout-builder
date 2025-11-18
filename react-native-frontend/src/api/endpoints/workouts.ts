import { apiClient } from "../client"
import { ApiResponse } from "../types"
import { ApiUserResponses, WorkoutPlan } from "../../types"

/**
 * Normalizes the final plan - handles both cases:
 * 1. When stream_response=True: backend returns a tuple [plan, metadata]
 * 2. When stream_response=False: backend returns just the plan object
 *
 * Always extracts the plan object and disregards metadata.
 */
const normalizeFinalPlan = (finalPlan: any): WorkoutPlan | null => {
  if (!finalPlan) return null

  // If it's an array (tuple from backend when stream_response=True),
  // extract the first element (the actual plan) and ignore metadata
  if (Array.isArray(finalPlan)) {
    if (finalPlan.length === 0) {
      console.warn("Received empty array for final plan")
      return null
    }
    // Extract the first element (the plan) and ignore the rest (metadata)
    return finalPlan[0] as WorkoutPlan
  }

  // If it's already a single object (when stream_response=False), return as-is
  return finalPlan as WorkoutPlan
}

export async function generateWorkoutPlan(
  responses: ApiUserResponses
): Promise<{ session_id: string }> {
  const response = await apiClient.request<ApiResponse<unknown>>(
    "/generate_workout_plan",
    {
      method: "POST",
      body: JSON.stringify(responses),
    }
  )

  if (response.success && response.session_id) {
    return { session_id: response.session_id }
  }
  throw new Error(response.error || "Failed to start workout generation")
}

export async function getGenerationProgress(sessionId: string): Promise<any> {
  const response = await apiClient.request<ApiResponse<any>>(
    `/generation_progress/${sessionId}`
  )

  if (response.success) {
    return response.data
  }
  throw new Error(response.error || "Failed to get generation progress")
}

export async function getFinalPlan(sessionId: string): Promise<WorkoutPlan> {
  const response = await apiClient.request<ApiResponse<WorkoutPlan>>(
    `/get_final_plan/${sessionId}`
  )

  if (response.success && response.data) {
    const normalizedPlan = normalizeFinalPlan(response.data)
    if (!normalizedPlan) {
      throw new Error("Failed to normalize final plan")
    }
    return normalizedPlan
  }
  throw new Error(response.error || "Failed to get final plan")
}
