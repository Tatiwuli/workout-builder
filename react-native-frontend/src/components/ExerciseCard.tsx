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
  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={styles.header}
        onPress={onToggle}
        activeOpacity={0.7}
      >
        <Text style={styles.exerciseName}>{exercise.exercise_name}</Text>
        <Text style={styles.expandIcon}>{isExpanded ? "▼" : "▶"}</Text>
      </TouchableOpacity>

      {isExpanded && (
        <View style={styles.details}>
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Setup:</Text>
            <Text style={styles.sectionText}>{exercise.setup_notes}</Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Execution:</Text>
            <Text style={styles.sectionText}>{exercise.execution_notes}</Text>
          </View>

          {exercise.media_url && (
            <View style={styles.mediaContainer}>
              <Text style={styles.sectionTitle}>Demo:</Text>
              <Image
                source={{ uri: exercise.media_url }}
                style={styles.media}
                resizeMode="contain"
              />
            </View>
          )}
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
    justifyContent: "space-between",
    alignItems: "center",
    padding: 16,
    backgroundColor: "#ffffff",
  },
  exerciseName: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#333333",
    flex: 1,
  },
  expandIcon: {
    fontSize: 16,
    color: "#007AFF",
    fontWeight: "bold",
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
  mediaContainer: {
    marginTop: 8,
  },
  media: {
    width: "100%",
    height: 200,
    borderRadius: 8,
    marginTop: 8,
  },
})

export default ExerciseCard
