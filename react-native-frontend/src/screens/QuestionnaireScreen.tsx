import React, { useMemo, useState } from "react"
import {
  View,
  StyleSheet,
  ScrollView,
  Alert,
  Platform,
  TouchableOpacity,
  Text,
} from "react-native"

const showAlert = (
  title: string,
  message: string,
  buttons?: { text: string; onPress?: () => void }[]
) => {
  if (Platform.OS === "web") {
    const combined = title ? `${title}\n\n${message}` : message
    const webAlert =
      (typeof window !== "undefined" &&
        typeof window.alert === "function" &&
        window.alert.bind(window)) ||
      (typeof globalThis !== "undefined" &&
        typeof (globalThis as { alert?: (msg: string) => void }).alert ===
          "function" &&
        (globalThis as { alert: (msg: string) => void }).alert.bind(globalThis))

    if (webAlert) {
      webAlert(combined)
      buttons?.[0]?.onPress?.()
      return
    }
  }

  Alert.alert(title, message, buttons)
}
import { generateWorkoutPlan } from "../api/endpoints/workouts"
import { StackNavigationProp } from "@react-navigation/stack"
import { RootStackParamList } from "../../App"
import {
  QUESTIONS,
  QuestionnaireState,
  UserResponse,
  ProcessedResponses,
  ApiUserResponses,
  WorkoutGenerationResponse,
  MUSCLE_GOAL_OPTIONS,
} from "../types"
import MuscleSelection from "../components/MuscleSelection"
import Questionnaire from "../components/Questionnaire"
import MuscleGoalSelector from "../components/MuscleGoalSelector"

type QuestionnaireScreenNavigationProp = StackNavigationProp<
  RootStackParamList,
  "Questionnaire"
>

interface Props {
  navigation: QuestionnaireScreenNavigationProp
}

const QuestionnaireScreen: React.FC<Props> = ({ navigation }) => {
  const [responses, setResponses] = useState<UserResponse>({})
  const [questionIndex, setQuestionIndex] = useState(0)
  const [selectedMuscles, setSelectedMuscles] = useState<string[]>([])
  const [workflowStage, setWorkflowStage] = useState<
    "muscle_selection" | "questionnaire" // different rendering
  >("muscle_selection")
  const [isGeneratingPlan, setIsGeneratingPlan] = useState(false)
  const [muscleGoals, setMuscleGoals] = useState<Record<string, string[]>>({})

  const musclesRequiringGoals = useMemo(
    () =>
      selectedMuscles.filter(
        (muscle) => (MUSCLE_GOAL_OPTIONS[muscle] || []).length > 0
      ),
    [selectedMuscles]
  )

  const handleMuscleToggle = (muscle: string) => {
    setSelectedMuscles((prev) => {
      if (prev.includes(muscle)) {
        setMuscleGoals((currentGoals) => {
          if (!currentGoals[muscle]) {
            return currentGoals
          }
          const updated = { ...currentGoals }
          delete updated[muscle]
          return updated
        })
        // unselect if user re-clicks a selected muscle
        return prev.filter((m) => m !== muscle)
      } else {
        if (prev.length >= 4) {
          showAlert(
            "Selection Limit",
            "You can only select up to 4 muscle groups.",
            [{ text: "Gotcha!" }]
          )
          return prev
        }
        return [...prev, muscle]
      }
    })
  }

  const handleSelectAll = (muscles: string[]) => {
    setSelectedMuscles((prev) => {
      const newSelection = [...new Set([...prev, ...muscles])]
      if (newSelection.length > 4) {
        showAlert(
          "Selection Limit",
          "You can only select up to 4 muscle groups. Please deselect some muscles first.",
          [{ text: "Gotcha!" }]
        )
        return prev
      }
      return newSelection
    })
  }

  const handleDeselectAll = (muscles: string[]) => {
    setSelectedMuscles((prev) => prev.filter((m) => !muscles.includes(m)))
    setMuscleGoals((currentGoals) => {
      const updated = { ...currentGoals }
      muscles.forEach((muscle) => {
        if (updated[muscle]) {
          delete updated[muscle]
        }
      })
      return updated
    })
  }

  const handleConfirmMuscleSelection = () => {
    if (selectedMuscles.length === 0) {
      console.log("Showing alert for 0 muscles selected")
      showAlert("Error", "Please select at least one muscle group.", [
        { text: "Gotcha!" },
      ])
      return
    }
    if (selectedMuscles.length > 4) {
      console.log("Showing alert for more than 4 muscles selected")
      showAlert("Error", "Please select up to 4 muscle groups.", [
        { text: "Gotcha!" },
      ])
      return
    }

    console.log("Proceeding to questionnaire stage")
    setWorkflowStage("questionnaire")
    setQuestionIndex(0)
    setResponses({})
    setMuscleGoals((currentGoals) => {
      const pruned: Record<string, string[]> = {}
      selectedMuscles.forEach((muscle) => {
        if (currentGoals[muscle]?.length) {
          pruned[muscle] = currentGoals[muscle]
        }
      })
      return pruned
    })
  }

  const handleConfirmMuscleGoals = () => {
    const missingGoalMuscles = musclesRequiringGoals.filter(
      (muscle) => !(muscleGoals[muscle] && muscleGoals[muscle].length > 0)
    )

    if (missingGoalMuscles.length > 0) {
      showAlert(
        "Incomplete Goals",
        `Please choose a goal for: ${missingGoalMuscles.join(", ")}.`,
        [{ text: "On it!" }]
      )
      setQuestionIndex(0)
      return
    }

    setQuestionIndex((prev) => (prev <= 0 ? 1 : prev))
  }

  const handleQuestionAnswer = (answer: string) => {
    if (questionIndex === 0) {
      return
    }
    const currentQuestion = QUESTIONS[questionIndex - 1]

    const newResponses = { ...responses, [currentQuestion]: answer }

    if (questionIndex < QUESTIONS.length) {
      setResponses(newResponses)
      setQuestionIndex((prev) => prev + 1)
    } else {
      // Last question answered - just save the responses
      setResponses(newResponses)
    }
  }

  const handleGenerateWorkoutPlan = async () => {
    const missingGoalMuscles = musclesRequiringGoals.filter(
      (muscle) => !(muscleGoals[muscle] && muscleGoals[muscle].length > 0)
    )

    if (missingGoalMuscles.length > 0) {
      showAlert(
        "Incomplete Goals",
        `Please choose a goal for: ${missingGoalMuscles.join(", ")}.`,
        [{ text: "On it!" }]
      )
      return
    }

    const processedResponses: ProcessedResponses = {
      frequency: responses.Frequency || "",
      duration: responses.Duration || "",
      experience: responses.Experience || "",
      selectedMuscles: selectedMuscles,
      muscleGoals,
    }

    setIsGeneratingPlan(true)

    // Prepare API request data
    const apiData: ApiUserResponses = {
      muscle_groups: processedResponses.selectedMuscles,
      frequency: processedResponses.frequency,
      duration: parseInt(
        processedResponses.duration.replace(" minutes", "") || "60"
      ),
      experience: processedResponses.experience,
      muscle_goals: musclesRequiringGoals.reduce<Record<string, string[]>>(
        (acc, muscle) => {
          const goals = muscleGoals[muscle]
          if (goals?.length) {
            acc[muscle] = goals
          }
          return acc
        },
        {}
      ),
      muscle_frequencies: {},
    }

    console.log("Starting workout generation with data:", processedResponses)
    console.log("API request data:", apiData)

    try {
      const response: WorkoutGenerationResponse =
        await generateWorkoutPlan(apiData)
      console.log("Backend triggered:", response)

      // Check if we got a session_id for polling
      if (response?.session_id) {
        console.log(
          "Workout generation started successfully! Session:",
          response.session_id
        )

        // Navigate to WorkoutGeneration screen with sessionId
        navigation.navigate("WorkoutGeneration", {
          sessionId: response.session_id,
        })

        // Reset loading state after navigation attempt
        setIsGeneratingPlan(false)
      } else {
        console.log("Invalid response received:", response)
        throw new Error("Invalid response from server")
      }
    } catch (error) {
      console.error("Failed to trigger workout generation:", error)
      setIsGeneratingPlan(false)

      showAlert(
        "Error",
        `Failed to start workout generation: ${
          error instanceof Error ? error.message : "Unknown error"
        }`,
        [{ text: "Gotcha!" }]
      )
    }
  }

  const renderMuscleSelection = () => (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={true}
        bounces={false}
        nestedScrollEnabled={true}
        scrollEnabled={true}
        keyboardShouldPersistTaps="handled"
      >
        <MuscleSelection
          selectedMuscles={selectedMuscles}
          onMuscleSelect={handleMuscleToggle}
          onSelectAll={handleSelectAll}
          onDeselectAll={handleDeselectAll}
          onConfirmSelection={handleConfirmMuscleSelection}
        />
      </ScrollView>
    </View>
  )

  const renderMuscleGoalsStep = () => (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={true}
        bounces={false}
        nestedScrollEnabled={true}
        scrollEnabled={true}
        keyboardShouldPersistTaps="handled"
      >
        <MuscleGoalSelector
          selectedMuscles={selectedMuscles}
          muscleGoals={muscleGoals}
          onGoalToggle={(muscle: string, goal: string) =>
            setMuscleGoals((currentGoals) => {
              const existing = currentGoals[muscle] || []
              const isSelected = existing.includes(goal)
              const updatedGoals = isSelected
                ? existing.filter((item) => item !== goal)
                : [...existing, goal]

              const next: Record<string, string[]> = {
                ...currentGoals,
                [muscle]: updatedGoals,
              }

              if (next[muscle].length === 0) {
                delete next[muscle]
              }

              return next
            })
          }
        />
        <TouchableOpacity
          style={styles.primaryButton}
          onPress={handleConfirmMuscleGoals}
          activeOpacity={0.8}
        >
          <Text style={styles.primaryButtonText}>Continue</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  )

  const renderQuestionnaire = () => (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={true}
        bounces={false}
        nestedScrollEnabled={true}
        scrollEnabled={true}
        keyboardShouldPersistTaps="handled"
      >
        <Questionnaire
          questionIndex={questionIndex - 1}
          responses={responses}
          onQuestionAnswer={handleQuestionAnswer}
          onGenerateWorkoutPlan={handleGenerateWorkoutPlan}
          isGeneratingPlan={isGeneratingPlan}
        />
      </ScrollView>
    </View>
  )

  return (
    <View style={styles.container}>
      {workflowStage === "muscle_selection" && renderMuscleSelection()}
      {workflowStage === "questionnaire" &&
        (questionIndex === 0 ? renderMuscleGoalsStep() : renderQuestionnaire())}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#ffffff",
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingBottom: 40,
  },
  primaryButton: {
    backgroundColor: "#007AFF",
    paddingVertical: 15,
    borderRadius: 25,
    alignItems: "center",
    marginTop: 16,
  },
  primaryButtonText: {
    color: "#ffffff",
    fontSize: 18,
    fontWeight: "bold",
  },
})

export default QuestionnaireScreen
