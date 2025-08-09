import { useState, useEffect } from "react"
import { apiService } from "../services/api"
import { WorkoutPlan } from "../types"

interface UseWorkoutPollingResult {
  isLoading: boolean
  error: string | null
  workoutPlan: WorkoutPlan | null
}

/**
 * Custom hook for polling workout generation progress
 * Polls the backend until generation is complete or fails
 * 
 * @param sessionId - The session ID returned from the initial API call
 * @returns Object with loading state, error state, and final workout plan
 */
export const useWorkoutPolling = (sessionId: string): UseWorkoutPollingResult => {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [workoutPlan, setWorkoutPlan] = useState<WorkoutPlan | null>(null)

  useEffect(() => {
    if (!sessionId) {
      setError("No session ID provided")
      setIsLoading(false)
      return
    }

    let isCancelled = false
    let timeoutId: NodeJS.Timeout

    const pollForResult = async () => {
      try {
        console.log(`Polling for session: ${sessionId}`)
        
        const progressResponse = await apiService.getGenerationProgress(sessionId)
        
        // Check if component was unmounted
        if (isCancelled) return

        const payload: any = progressResponse.data

        if (progressResponse.success && payload?.success) {
          const progressData = payload.data

          if (progressData?.status === "completed" && progressData?.final_plan) {
            console.log("Workout generation completed successfully!")
            setWorkoutPlan(progressData.final_plan)
            setIsLoading(false)
            return // Stop polling
          }

          if (progressData?.status === "error") {
            console.error("Workout generation failed:", progressData?.message)
            setError(progressData?.message || "Workout generation failed")
            setIsLoading(false)
            return // Stop polling
          }

          // Still in progress - schedule next poll
          if (progressData?.status === "running" || progressData?.status === "pending") {
            console.log("Generation still in progress, polling again in 3 seconds...")
            timeoutId = setTimeout(pollForResult, 3000)
          }
        } else {
          // Backend returned non-success, retry after longer delay
          console.warn("Backend returned non-success, retrying in 5 seconds...")
          timeoutId = setTimeout(pollForResult, 5000)
        }
      } catch (err) {
        console.error("Polling error:", err)
        
        if (isCancelled) return

        // Network error or other issue - retry after delay
        timeoutId = setTimeout(pollForResult, 5000)
      }
    }

    // Start polling
    pollForResult()

    // Cleanup function
    return () => {
      isCancelled = true
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
    }
  }, [sessionId])

  return {
    isLoading,
    error,
    workoutPlan,
  }
}
