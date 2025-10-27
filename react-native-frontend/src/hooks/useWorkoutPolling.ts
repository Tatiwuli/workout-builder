import { useState, useEffect } from "react"
import { apiService } from "../services/api"
import { WorkoutPlan } from "../types"

interface ProgressData {
  progress: number
  message: string
  status: string
  final_plan: WorkoutPlan | null
}

interface UseWorkoutPollingResult {
  isLoading: boolean
  error: string | null
  workoutPlan: WorkoutPlan | null
  progressData: ProgressData | null
  retry: () => void
}

/**
 * Custom hook for polling workout generation progress
 * Polls the backend until generation is complete or fails
 *
 * @param sessionId - The session ID returned from the initial API call
 * @returns Object with loading state, error state, final workout plan, and retry function
 * - isLoading: boolean indicating if generation is in progress
 * - error: string with error message or null if no error
 * - workoutPlan: the generated WorkoutPlan object or null if not ready
 * - retry: function to reset state and restart polling (useful for transient errors)
 */
export const useWorkoutPolling = (sessionId: string):     UseWorkoutPollingResult => {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [workoutPlan, setWorkoutPlan] = useState<WorkoutPlan | null>(null)
  const [progressData, setProgressData] = useState<ProgressData | null>(null)
  const [retryTrigger, setRetryTrigger] = useState(0)

  // Retry function that resets state and triggers re-polling
  const retry = () => {
    setError(null)
    setIsLoading(true)
    setWorkoutPlan(null)
    setProgressData(null)
    setRetryTrigger((prev) => prev + 1) // Trigger useEffect re-run
  }

  // three types of status: generating, failed, generated  workout plan
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

        const progressData = await apiService.getGenerationProgress(sessionId)
        console.log("progressData received:", progressData)

        // Check if component was unmounted
        if (isCancelled) return

       
        // Normalize payload in case backend returns { success, data }
        const payload: any =
          progressData &&
          (typeof (progressData as any).status !== "undefined" ||
            typeof (progressData as any).progress !== "undefined")
            ? progressData
            : (progressData as any)?.data ?? progressData

        console.log("Normalized status:", payload?.status)
        console.log("Normalized progress:", payload?.progress)
        console.log("Has final_plan:", !!payload?.final_plan)

        // Expose progress data for UI
        if (
          payload &&
          (typeof payload.progress !== "undefined" ||
            payload.message ||
            payload.status)
        ) {
          setProgressData({
            progress: Number(payload.progress) || 0,
            message: String(payload.message || "Processing..."),
            status: String(payload.status || "running"),
            final_plan: (payload.final_plan as WorkoutPlan) || null,
          })
        }

        // If completed and we already have final_plan in payload
        if (payload?.status === "completed" && payload?.final_plan) {
          console.log("Workout generation completed successfully!")
          console.log("Final plan:", payload.final_plan)
          setWorkoutPlan(payload.final_plan)
          setIsLoading(false)
          return // Stop polling
        }

        // If completed but no final_plan attached, try fetching it explicitly
        if (payload?.status === "completed" && !payload?.final_plan) {
          console.log(
            "Status completed but final_plan missing. Fetching via getFinalPlan..."
          )
          try {
            const finalPlan = await apiService.getFinalPlan(sessionId)
            if (!isCancelled) {
              setWorkoutPlan(finalPlan)
              setIsLoading(false)
            }
            return
          } catch (fetchErr) {
            console.error("Failed to fetch final plan:", fetchErr)
            // Fall through to retry shortly
          }
        }

        if (payload?.status === "error") {
          console.error("Workout generation failed:", payload?.message)
          setError(payload?.message || "Workout generation failed")
          setIsLoading(false)
          return // Stop polling
        }

        // Still in progress - schedule next poll
        if (payload?.status === "running" || payload?.status === "pending") {
          console.log(
            "Generation still in progress, polling again in 3 seconds..."
          )
          timeoutId = setTimeout(pollForResult, 3000)
        } else if (payload?.progress === 100) {
          // Some backends might only update progress to 100 without status
          console.log(
            "Progress is 100 but status not marked completed. Attempting to fetch final plan..."
          )
          try {
            const finalPlan = await apiService.getFinalPlan(sessionId)
            if (!isCancelled) {
              setWorkoutPlan(finalPlan)
              setIsLoading(false)
            }
            return
          } catch (fetchErr) {
            console.error(
              "Failed to fetch final plan on 100% progress:",
              fetchErr
            )
            console.log("Retrying in 3 seconds...")
            timeoutId = setTimeout(pollForResult, 3000)
          }
        } else {
          // Unexpected status - log and retry
          console.warn("Unexpected status received:", payload?.status)
          console.warn("Full payload:", payload)
          console.log("Retrying in 3 seconds...")
          timeoutId = setTimeout(pollForResult, 3000)
        }
      } catch (err) {
        console.error("Polling error:", err)

        if (isCancelled) return

        // API error (network issue, server error, etc.) - retry after delay
        console.warn("Polling failed, retrying in 5 seconds...")
        timeoutId = setTimeout(pollForResult, 5000)
      }

      // Safeguard: if no timeout was scheduled and polling hasn't stopped, schedule a default retry
      if (!isCancelled && !timeoutId && isLoading) {
        console.log(
          "No polling condition matched; scheduling default retry in 4 seconds..."
        )
        timeoutId = setTimeout(pollForResult, 4000)
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
  }, [sessionId, retryTrigger])

  return {
    isLoading,
    error,
    workoutPlan,
    progressData,
    retry,
  }
}
