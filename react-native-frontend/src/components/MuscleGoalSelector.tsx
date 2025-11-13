import React from "react"
import { View, Text, StyleSheet, TouchableOpacity } from "react-native"

import { MUSCLE_GOAL_OPTIONS } from "../types"

interface MuscleGoalSelectorProps {
  selectedMuscles: string[]
  muscleGoals: Record<string, string[]>
  onGoalToggle: (muscle: string, goal: string) => void
}

const MuscleGoalSelector: React.FC<MuscleGoalSelectorProps> = ({
  selectedMuscles,
  muscleGoals,
  onGoalToggle,
}) => {
  const musclesWithOptions = selectedMuscles.filter(
    (muscle) => (MUSCLE_GOAL_OPTIONS[muscle] || []).length > 0
  )

  if (musclesWithOptions.length === 0) {
    return null
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Set Your Muscle Goals 💪</Text>
      <Text style={styles.subtitle}>
        Pick one or more focus areas for each muscle group you selected.
      </Text>

      {musclesWithOptions.map((muscle) => {
        const options = MUSCLE_GOAL_OPTIONS[muscle] || []
        const selectedForMuscle = muscleGoals[muscle] || []

        return (
          <View key={muscle} style={styles.muscleContainer}>
            <Text style={styles.muscleTitle}>{muscle}</Text>
            <View style={styles.optionsContainer}>
              {options.map((option) => {
                const isSelected = selectedForMuscle.includes(option)
                return (
                  <TouchableOpacity
                    key={option}
                    style={[
                      styles.optionButton,
                      isSelected && styles.optionButtonSelected,
                    ]}
                    onPress={() => onGoalToggle(muscle, option)}
                    activeOpacity={0.7}
                  >
                    <Text
                      style={[
                        styles.optionText,
                        isSelected && styles.optionTextSelected,
                      ]}
                    >
                      {option}
                    </Text>
                  </TouchableOpacity>
                )
              })}
            </View>
          </View>
        )
      })}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 20,
    marginTop: 20,
  },
  title: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#333333",
    textAlign: "center",
    marginBottom: 6,
  },
  subtitle: {
    fontSize: 14,
    color: "#666666",
    textAlign: "center",
    marginBottom: 16,
  },
  muscleContainer: {
    backgroundColor: "#f8f9fa",
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  muscleTitle: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#333333",
    marginBottom: 12,
  },
  optionsContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  optionButton: {
    backgroundColor: "#ffffff",
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#dee2e6",
    paddingHorizontal: 14,
    paddingVertical: 8,
  },
  optionButtonSelected: {
    backgroundColor: "#007AFF",
    borderColor: "#007AFF",
  },
  optionText: {
    color: "#333333",
    fontSize: 14,
    fontWeight: "500",
  },
  optionTextSelected: {
    color: "#ffffff",
    fontWeight: "bold",
  },
})

export default MuscleGoalSelector
