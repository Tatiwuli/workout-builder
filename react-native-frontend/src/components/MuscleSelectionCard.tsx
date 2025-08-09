import React from "react"
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Dimensions,
} from "react-native"

const { width } = Dimensions.get("window")

interface MuscleSelectionCardProps { // Represent a muscle group card
  title: string
  muscles: string[]
  selectedMuscles: string[] // Selection state
  onMuscleSelect: (muscle: string) => void //Callback when a muscle is selected
  onSelectAll: () => void //Callback when all muscles ( of same group)are selected
  onDeselectAll: () => void //Callback when onSelectAll is deselected
}

const MuscleSelectionCard: React.FC<MuscleSelectionCardProps> = ({
  title,
  muscles,
  selectedMuscles,
  onMuscleSelect,
  onSelectAll,
  onDeselectAll,
}) => {
  const allSelected = muscles.every((muscle) =>
    selectedMuscles.includes(muscle)
  )
  const someSelected = muscles.some((muscle) =>
    selectedMuscles.includes(muscle)
  )

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.title}>{title}</Text>
        <View style={styles.selectAllContainer}>
          <TouchableOpacity
            style={[
              styles.selectAllButton,
              allSelected && styles.selectAllButtonActive,
            ]}
            onPress={allSelected ? onDeselectAll : onSelectAll}
          >
            <Text
              style={[
                styles.selectAllText,
                allSelected && styles.selectAllTextActive,
              ]}
            >
              {allSelected ? "Deselect All" : "Select All"}
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.musclesContainer}>
        {muscles.map((muscle) => {
          const isSelected = selectedMuscles.includes(muscle)
          return (
            <TouchableOpacity
              key={muscle}
              style={[
                styles.muscleButton,
                isSelected && styles.muscleButtonSelected,
              ]}
              onPress={() => onMuscleSelect(muscle)}
              activeOpacity={0.7}
            >
              <Text
                style={[
                  styles.muscleText,
                  isSelected && styles.muscleTextSelected,
                ]}
              >
                {muscle}
              </Text>
            </TouchableOpacity>
          )
        })}
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#f8f9fa",
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 3,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  title: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#333333",
  },
  selectAllContainer: {
    flexDirection: "row",
  },
  selectAllButton: {
    backgroundColor: "#e9ecef",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  selectAllButtonActive: {
    backgroundColor: "#007AFF",
  },
  selectAllText: {
    color: "#666666",
    fontSize: 12,
    fontWeight: "600",
  },
  selectAllTextActive: {
    color: "#ffffff",
  },
  musclesContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  muscleButton: {
    backgroundColor: "#ffffff",
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#dee2e6",
  },
  muscleButtonSelected: {
    backgroundColor: "#007AFF",
    borderColor: "#007AFF",
  },
  muscleText: {
    color: "#333333",
    fontSize: 14,
    fontWeight: "500",
  },
  muscleTextSelected: {
    color: "#ffffff",
    fontWeight: "bold",
  },
})

export default MuscleSelectionCard
