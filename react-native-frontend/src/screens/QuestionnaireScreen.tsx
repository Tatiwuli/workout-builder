import React, { useState } from "react"
import { View, StyleSheet, ScrollView, Alert } from "react-native"
import { apiService } from "../services/api"
import { StackNavigationProp } from "@react-navigation/stack"
import { RootStackParamList } from "../../App"
import {
  QUESTIONS,
  QuestionnaireState,
  UserResponse,
  ProcessedResponses,
  ApiUserResponses,
} from "../types"
import MuscleSelection from "../components/MuscleSelection"
import Questionnaire from "../components/Questionnaire"

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
    "muscle_selection" | "questionnaire"
  >("muscle_selection")
  const [isGeneratingPlan, setIsGeneratingPlan] = useState(false)

  const handleMuscleToggle = (muscle: string) => {
    setSelectedMuscles((prev) =>
      prev.includes(muscle)
        ? prev.filter((m) => m !== muscle)
        : [...prev, muscle]
    )
  }

  const handleSelectAll = (muscles: string[]) => {
    setSelectedMuscles((prev) => [...new Set([...prev, ...muscles])])
  }

  const handleDeselectAll = (muscles: string[]) => {
    setSelectedMuscles((prev) => prev.filter((m) => !muscles.includes(m)))
  }

  const handleConfirmMuscleSelection = () => {
    if (selectedMuscles.length === 0) {
      Alert.alert("Error", "Please select at least one muscle group.")
      return
    }
    if (selectedMuscles.length > 4) {
      Alert.alert("Error", "Please select up to 4 muscle groups.")
      return
    }

    setWorkflowStage("questionnaire")
    setQuestionIndex(0)
    setResponses({})
  }

  const handleQuestionAnswer = (answer: string) => {
    const currentQuestion = QUESTIONS[questionIndex]
    const newResponses = { ...responses, [currentQuestion]: answer }

    if (questionIndex < QUESTIONS.length - 1) {
      setResponses(newResponses)
      setQuestionIndex((prev) => prev + 1)
    } else {
      // Last question answered - just save the responses
      setResponses(newResponses)
    }
  }

  const handleGenerateWorkoutPlan = async () => {
    const processedResponses: ProcessedResponses = {
      goal: responses.Goal || "",
      frequency: responses.Frequency || "",
      duration: responses.Duration || "",
      experience: responses.Experience || "",
      selectedMuscles: selectedMuscles,
    }

    setIsGeneratingPlan(true)

    try {
      // Prepare API request data
      const apiData: ApiUserResponses = {
        muscle_groups: processedResponses.selectedMuscles,
        goal: processedResponses.goal,
        frequency: processedResponses.frequency,
        duration: parseInt(
          processedResponses.duration.replace(" minutes", "") || "60"
        ),
        experience: processedResponses.experience,
        muscle_goals: {},
        muscle_frequencies: {},
      }

      console.log("Starting workout generation with data:", processedResponses)
      console.log("API request data:", apiData)

      // Make API call to start generation
      const response = await apiService.generateWorkoutPlan(apiData)
      console.log("Backend triggered:", response)

      const backendPayload: any = response.data

      if (
        response.success &&
        backendPayload?.success &&
        backendPayload?.session_id
      ) {
        console.log(
          "Workout generation started successfully! Session:",
          backendPayload.session_id
        )

        // Navigate to WorkoutGeneration screen with sessionId
        navigation.navigate("WorkoutGeneration", {
          sessionId: backendPayload.session_id,
        })
      } else {
        throw new Error(
          backendPayload?.error ||
            response.error ||
            "Failed to start workout generation"
        )
      }
    } catch (error) {
      console.error("Failed to trigger workout generation:", error)
      setIsGeneratingPlan(false)

      Alert.alert(
        "Error",
        `Failed to start workout generation: ${
          error instanceof Error ? error.message : "Unknown error"
        }`,
        [{ text: "OK" }]
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
          questionIndex={questionIndex}
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
      {workflowStage === "muscle_selection"
        ? renderMuscleSelection()
        : renderQuestionnaire()}
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
})

export default QuestionnaireScreen
