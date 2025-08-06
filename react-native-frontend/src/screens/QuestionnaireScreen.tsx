import React, { useState, useEffect } from "react"
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Platform,
} from "react-native"
import { SafeAreaView } from "react-native-safe-area-context"
import { StackNavigationProp } from "@react-navigation/stack"
import { RootStackParamList } from "../../App"
import {
  PULL_OPTIONS,
  PUSH_OPTIONS,
  LEG_OPTIONS,
  QUESTIONS,
  QuestionnaireState,
  UserResponse,
  ProcessedResponses,
} from "../types"
import MuscleSelectionCard from "../components/MuscleSelectionCard"
import QuestionCard from "../components/QuestionCard"

type QuestionnaireScreenNavigationProp = StackNavigationProp<
  RootStackParamList,
  "Questionnaire"
>

interface Props {
  navigation: QuestionnaireScreenNavigationProp
}

const QuestionnaireScreen: React.FC<Props> = ({ navigation }) => {
  const [state, setState] = useState<QuestionnaireState>({
    responses: {},
    questionIndex: 0,
    selectedMuscles: [],
    workflowStage: "muscle_selection",
    isGeneratingPlan: false,
    planGenerated: false,
  })

  const questionOptions = {
    Goal: ["Build Muscle", "Lose Fat", "Improve Strength", "General Fitness"],
    Frequency: [
      "2-3 times per week",
      "4-5 times per week",
      "6+ times per week",
    ],
    Duration: ["30-45 minutes", "45-60 minutes", "60+ minutes"],
    Experience: ["Beginner", "Intermediate", "Advanced"],
  }

  const handleMuscleToggle = (muscle: string) => {
    setState((prev) => ({
      ...prev,
      selectedMuscles: prev.selectedMuscles.includes(muscle)
        ? prev.selectedMuscles.filter((m) => m !== muscle)
        : [...prev.selectedMuscles, muscle],
    }))
  }

  const handleSelectAll = (muscles: string[]) => {
    setState((prev) => ({
      ...prev,
      selectedMuscles: [...new Set([...prev.selectedMuscles, ...muscles])],
    }))
  }

  const handleDeselectAll = (muscles: string[]) => {
    setState((prev) => ({
      ...prev,
      selectedMuscles: prev.selectedMuscles.filter((m) => !muscles.includes(m)),
    }))
  }

  const handleConfirmMuscleSelection = () => {
    if (state.selectedMuscles.length === 0) {
      Alert.alert("Error", "Please select at least one muscle group.")
      return
    }
    if (state.selectedMuscles.length > 4) {
      Alert.alert("Error", "Please select up to 4 muscle groups.")
      return
    }

    setState((prev) => ({
      ...prev,
      workflowStage: "questionnaire",
      questionIndex: 0,
      responses: {},
    }))
  }

  const handleQuestionAnswer = (answer: string) => {
    const currentQuestion = QUESTIONS[state.questionIndex]
    const newResponses = { ...state.responses, [currentQuestion]: answer }

    if (state.questionIndex < QUESTIONS.length - 1) {
      setState((prev) => ({
        ...prev,
        responses: newResponses,
        questionIndex: prev.questionIndex + 1,
      }))
    } else {
      // Last question answered
      const processedResponses: ProcessedResponses = {
        goal: newResponses.Goal || "",
        frequency: newResponses.Frequency || "",
        duration: newResponses.Duration || "",
        experience: newResponses.Experience || "",
        selectedMuscles: state.selectedMuscles,
      }

      setState((prev) => ({
        ...prev,
        responses: newResponses,
        processedResponses,
        isGeneratingPlan: true,
      }))

      // Simulate plan generation (replace with actual API call)
      setTimeout(() => {
        setState((prev) => ({
          ...prev,
          isGeneratingPlan: false,
          planGenerated: true,
        }))
        navigation.navigate("WorkoutPlan")
      }, 2000)
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
        <View style={styles.content}>
          <Text style={styles.title}>Select Target Muscle Groups</Text>
          <Text style={styles.subtitle}>
            Choose up to 4 muscle groups you want to focus on
          </Text>

          <MuscleSelectionCard
            title="Pull Muscles"
            muscles={PULL_OPTIONS}
            selectedMuscles={state.selectedMuscles}
            onMuscleToggle={handleMuscleToggle}
            onSelectAll={() => handleSelectAll(PULL_OPTIONS)}
            onDeselectAll={() => handleDeselectAll(PULL_OPTIONS)}
          />

          <MuscleSelectionCard
            title="Push Muscles"
            muscles={PUSH_OPTIONS}
            selectedMuscles={state.selectedMuscles}
            onMuscleToggle={handleMuscleToggle}
            onSelectAll={() => handleSelectAll(PUSH_OPTIONS)}
            onDeselectAll={() => handleDeselectAll(PUSH_OPTIONS)}
          />

          <MuscleSelectionCard
            title="Leg Muscles"
            muscles={LEG_OPTIONS}
            selectedMuscles={state.selectedMuscles}
            onMuscleToggle={handleMuscleToggle}
            onSelectAll={() => handleSelectAll(LEG_OPTIONS)}
            onDeselectAll={() => handleDeselectAll(LEG_OPTIONS)}
          />

          <View style={styles.selectedMusclesContainer}>
            <Text style={styles.selectedTitle}>Selected Muscles:</Text>
            <Text style={styles.selectedMuscles}>
              {state.selectedMuscles.length > 0
                ? state.selectedMuscles.join(", ")
                : "None selected"}
            </Text>
          </View>

          <TouchableOpacity
            style={styles.confirmButton}
            onPress={handleConfirmMuscleSelection}
            activeOpacity={0.8}
          >
            <Text style={styles.confirmButtonText}>Confirm Selection</Text>
          </TouchableOpacity>
        </View>
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
        <View style={styles.content}>
          <View style={styles.progressContainer}>
            <Text style={styles.progressText}>
              Question {state.questionIndex + 1} of {QUESTIONS.length}
            </Text>
            <View style={styles.progressBar}>
              <View
                style={[
                  styles.progressFill,
                  {
                    width: `${
                      ((state.questionIndex + 1) / QUESTIONS.length) * 100
                    }%`,
                  },
                ]}
              />
            </View>
          </View>

          <QuestionCard
            question={`What is your primary ${QUESTIONS[state.questionIndex]}?`}
            options={
              questionOptions[
                QUESTIONS[state.questionIndex] as keyof typeof questionOptions
              ]
            }
            selectedOption={
              state.responses[
                QUESTIONS[state.questionIndex] as keyof UserResponse
              ]
            }
            onOptionSelect={handleQuestionAnswer}
          />

          {state.isGeneratingPlan && (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#007AFF" />
              <Text style={styles.loadingText}>
                Generating your personalized workout plan...
              </Text>
            </View>
          )}
        </View>
      </ScrollView>
    </View>
  )

  return (
    <View style={styles.container}>
      {state.workflowStage === "muscle_selection"
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
  content: {
    padding: 20,
    paddingTop: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#333333",
    textAlign: "center",
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: "#666666",
    textAlign: "center",
    marginBottom: 30,
  },
  selectedMusclesContainer: {
    backgroundColor: "#f8f9fa",
    padding: 16,
    borderRadius: 12,
    marginBottom: 20,
  },
  selectedTitle: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#333333",
    marginBottom: 8,
  },
  selectedMuscles: {
    fontSize: 14,
    color: "#666666",
  },
  confirmButton: {
    backgroundColor: "#007AFF",
    paddingVertical: 15,
    borderRadius: 25,
    alignItems: "center",
    shadowColor: "#007AFF",
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  confirmButtonText: {
    color: "#ffffff",
    fontSize: 18,
    fontWeight: "bold",
  },
  progressContainer: {
    marginBottom: 30,
  },
  progressText: {
    fontSize: 16,
    color: "#333333",
    textAlign: "center",
    marginBottom: 10,
  },
  progressBar: {
    height: 4,
    backgroundColor: "#e9ecef",
    borderRadius: 2,
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    backgroundColor: "#007AFF",
    borderRadius: 2,
  },
  loadingContainer: {
    alignItems: "center",
    marginTop: 40,
  },
  loadingText: {
    color: "#333333",
    fontSize: 16,
    marginTop: 16,
    textAlign: "center",
  },
})

export default QuestionnaireScreen
