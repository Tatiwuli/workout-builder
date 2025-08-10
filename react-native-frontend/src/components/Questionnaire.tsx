import React from "react"
import { View, Text, StyleSheet, TouchableOpacity } from "react-native"
import { QUESTIONS, UserResponse } from "../types"
import QuestionCard from "./QuestionCard"

interface QuestionnaireProps {
  questionIndex: number
  responses: UserResponse
  onQuestionAnswer: (answer: string) => void
  onGenerateWorkoutPlan: () => void
  isGeneratingPlan: boolean
}

const Questionnaire: React.FC<QuestionnaireProps> = ({
  questionIndex,
  responses,
  onQuestionAnswer,
  onGenerateWorkoutPlan,
  isGeneratingPlan,
}) => {
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

  return (
    <View style={styles.container}>
      <View style={styles.progressContainer}>
        <Text style={styles.progressText}>
          Question {questionIndex + 1} of {QUESTIONS.length}
        </Text>
        <View style={styles.progressBar}>
          <View
            style={[
              styles.progressFill,
              {
                width: `${((questionIndex + 1) / QUESTIONS.length) * 100}%`,
              },
            ]}
          />
        </View>
      </View>

      <QuestionCard
        question={`What is your primary ${QUESTIONS[questionIndex]}?`}
        options={
          questionOptions[
            QUESTIONS[questionIndex] as keyof typeof questionOptions
          ]
        }
        selectedOption={
          responses[QUESTIONS[questionIndex] as keyof UserResponse]
        }
        onOptionSelect={onQuestionAnswer}
      />

      {/* Show Generate Workout Plan button on the last question */}
      {questionIndex === QUESTIONS.length - 1 && (
        <View style={styles.generateButtonContainer}>
          <TouchableOpacity
            style={[
              styles.generateButton,
              isGeneratingPlan && styles.generateButtonDisabled,
            ]}
            onPress={isGeneratingPlan ? undefined : onGenerateWorkoutPlan}
            activeOpacity={isGeneratingPlan ? 1 : 0.8}
            disabled={isGeneratingPlan}
          >
            <Text style={styles.generateButtonText}>
              {isGeneratingPlan
                ? "Starting Generation..."
                : "Generate Workout Plan"}
            </Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    paddingTop: 20,
  },
  progressContainer: {
    marginBottom: 30,
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
  progressText: {
    fontSize: 14,
    color: "#666666",
    textAlign: "center",
    marginBottom: 8,
  },
  generateButtonContainer: {
    marginTop: 30,
    alignItems: "center",
  },
  generateButton: {
    backgroundColor: "#007AFF",
    paddingVertical: 15,
    paddingHorizontal: 30,
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
  generateButtonDisabled: {
    backgroundColor: "#ccc",
    elevation: 2,
    shadowOpacity: 0.1,
  },
  generateButtonText: {
    color: "#ffffff",
    fontSize: 18,
    fontWeight: "bold",
  },
})

export default Questionnaire
