import React from "react"
import { View, Text, StyleSheet, TouchableOpacity } from "react-native"
import { PULL_OPTIONS, PUSH_OPTIONS, LEG_OPTIONS } from "../types"
import MuscleSelectionCard from "./MuscleSelectionCard"

interface MuscleSelectionProps {
  selectedMuscles: string[]
  onMuscleSelect: (muscle: string) => void
  onSelectAll: (muscles: string[]) => void
  onDeselectAll: (muscles: string[]) => void
  onConfirmSelection: () => void
}

const MuscleSelection: React.FC<MuscleSelectionProps> = ({
  selectedMuscles,
  onMuscleSelect,
  onSelectAll,
  onDeselectAll,
  onConfirmSelection,
}) => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Select Target Muscle Groups</Text>
      <Text style={styles.subtitle}>
        Choose up to 4 muscle groups you want to focus on
      </Text>

      <MuscleSelectionCard
        title="Pull Muscles"
        muscles={PULL_OPTIONS}
        selectedMuscles={selectedMuscles}
        onMuscleSelect={onMuscleSelect}
        onSelectAll={() => onSelectAll(PULL_OPTIONS)}
        onDeselectAll={() => onDeselectAll(PULL_OPTIONS)}
      />

      <MuscleSelectionCard
        title="Push Muscles"
        muscles={PUSH_OPTIONS}
        selectedMuscles={selectedMuscles}
        onMuscleSelect={onMuscleSelect}
        onSelectAll={() => onSelectAll(PUSH_OPTIONS)}
        onDeselectAll={() => onDeselectAll(PUSH_OPTIONS)}
      />

      <MuscleSelectionCard
        title="Leg Muscles"
        muscles={LEG_OPTIONS}
        selectedMuscles={selectedMuscles}
        onMuscleSelect={onMuscleSelect}
        onSelectAll={() => onSelectAll(LEG_OPTIONS)}
        onDeselectAll={() => onDeselectAll(LEG_OPTIONS)}
      />

      <View style={styles.selectedMusclesContainer}>
        <Text style={styles.selectedTitle}>Selected Muscles:</Text>
        <Text style={styles.selectedMuscles}>
          {selectedMuscles.length > 0
            ? selectedMuscles.join(", ")
            : "None selected"}
        </Text>
      </View>

      <TouchableOpacity
        style={styles.confirmButton}
        onPress={onConfirmSelection}
        activeOpacity={0.8}
      >
        <Text style={styles.confirmButtonText}>Confirm Selection</Text>
      </TouchableOpacity>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
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
})

export default MuscleSelection
