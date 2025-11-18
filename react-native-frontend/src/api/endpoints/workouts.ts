import { apiClient } from "../client"
import { ApiResponse } from "../types"
import { ApiUserResponses, WorkoutPlan } from "../../types"

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

/**
 * Normalizes the final plan - handles case where backend returns a tuple [plan, metadata]
 * instead of just the plan object. This is a defensive check for a backend bug.
 */
const normalizeFinalPlan = (finalPlan: any): WorkoutPlan | null => {
  if (!finalPlan) return null

  // If it's an array (tuple from backend), extract the first element (the actual plan)
  if (Array.isArray(finalPlan) && finalPlan.length > 0) {
    console.warn(
      "Received array instead of plan object, extracting first element"
    )
    return finalPlan[0] as WorkoutPlan
  }

  return finalPlan as WorkoutPlan
}

export async function getFinalPlan(sessionId: string): Promise<WorkoutPlan> {
  const response = await apiClient.request<ApiResponse<WorkoutPlan>>(
    `/get_final_plan/${sessionId}`
  )

  if (response.success && response.data) {
    const normalized = normalizeFinalPlan(response.data)
    if (!normalized) {
      throw new Error("Invalid workout plan data received")
    }
    return normalized
  }
  throw new Error(response.error || "Failed to get final plan")
}
