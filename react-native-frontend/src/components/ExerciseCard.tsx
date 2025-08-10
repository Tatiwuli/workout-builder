import React from "react"
import { View, Text, StyleSheet, TouchableOpacity, Image } from "react-native"
import { Exercise } from "../types"

interface ExerciseCardProps {
  exercise: Exercise
  isExpanded?: boolean
  onToggle?: () => void
}

const ExerciseCard: React.FC<ExerciseCardProps> = ({
  exercise,
  isExpanded = false,
  onToggle,
}) => {
  console.log("ExerciseCard received data:", JSON.stringify(exercise, null, 2))

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={styles.header}
        onPress={onToggle}
        activeOpacity={0.7}
      >
        <View style={styles.titleContainer}>
          <Text style={styles.exerciseName}>{exercise.exercise_name}</Text>
          {exercise.media_url && (
            <Image
              source={{ uri: exercise.media_url }}
              style={styles.thumbnail}
              resizeMode="contain"
            />
          )}
        </View>

        <Text style={styles.expandIcon}>{isExpanded ? "▼" : "▶"}</Text>
      </TouchableOpacity>

      {isExpanded && (
        <View style={styles.details}>
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Setup:</Text>
            <Text style={styles.sectionText}>{exercise.setup}</Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Execution:</Text>
            <Text style={styles.sectionText}>{exercise.execution}</Text>
          </View>
        </View>
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: "#f8f9fa",
    borderRadius: 8,
    marginBottom: 12,
    overflow: "hidden",
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    padding: 16,
    backgroundColor: "#ffffff",
  },
  titleContainer: {
    flexDirection: "row",
    alignItems: "center",
    flex: 1,
  },
  exerciseName: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#333333",
    flexShrink: 1,
  },
  thumbnail: {
    width: 100,
    height: 100,
    borderRadius: 8,
    marginLeft: 8,
  },
  expandIcon: {
    fontSize: 16,
    color: "#007AFF",
    fontWeight: "bold",
    marginLeft: 8,
  },
  details: {
    padding: 16,
  },
  section: {
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#007AFF",
    marginBottom: 4,
  },
  sectionText: {
    fontSize: 14,
    color: "#666666",
    lineHeight: 20,
  },
})

export default ExerciseCard
