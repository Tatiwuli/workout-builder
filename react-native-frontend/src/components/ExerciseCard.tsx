import React, { useState } from "react"
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
  const [isAlternativeExpanded, setIsAlternativeExpanded] = useState(false)

  const renderExecution = (execution: string | string[]) => {
    if (Array.isArray(execution)) {
      // if it's formatted as a list
      return execution.map(
        (
          step,
          index // each step starts in a new line
        ) => (
          <Text key={index} style={styles.executionStep}>
            {step}
          </Text>
        )
      )
    }
    return <Text style={styles.sectionText}>{execution}</Text>
  }

  const hasAlternativeExercise =
    exercise.alternative_exercise && exercise.alternative_exercise.trim() !== ""

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={[styles.header, isExpanded && styles.headerExpanded]}
        onPress={onToggle}
        activeOpacity={0.6}
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
      </TouchableOpacity>

      {isExpanded && (
        <View style={styles.details}>
          {exercise.weight && (
            <View style={styles.fieldRow}>
              <Text style={styles.fieldLabel}>Weight:</Text>
              <Text style={styles.fieldValue}>{exercise.weight}</Text>
            </View>
          )}

          {exercise.sets && (
            <View style={styles.fieldRow}>
              <Text style={styles.fieldLabel}>Sets:</Text>
              <Text style={styles.fieldValue}>
                {typeof exercise.sets === "number"
                  ? exercise.sets.toString()
                  : exercise.sets}
              </Text>
            </View>
          )}

          {exercise.reps && (
            <View style={styles.fieldRow}>
              <Text style={styles.fieldLabel}>Reps:</Text>
              <Text style={styles.fieldValue}>
                {typeof exercise.reps === "number"
                  ? exercise.reps.toString()
                  : exercise.reps}
              </Text>
            </View>
          )}

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Setup:</Text>
            <Text style={styles.sectionText}>{exercise.setup}</Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Execution:</Text>
            {renderExecution(exercise.execution)}

            {exercise.additional_tips &&
              exercise.additional_tips.trim() !== "" &&
              exercise.additional_tips.trim().toLowerCase() !== "none" && (
                <View style={styles.tipsContainer}>
                  <Text style={styles.tipsText}>
                    ☝️{exercise.additional_tips}
                  </Text>
                </View>
              )}
          </View>

          {hasAlternativeExercise && (
            <View style={styles.alternativeContainer}>
              <TouchableOpacity
                style={[
                  styles.alternativeHeader,
                  isAlternativeExpanded && styles.alternativeHeaderExpanded,
                ]}
                onPress={() => setIsAlternativeExpanded(!isAlternativeExpanded)}
                activeOpacity={0.6}
              >
                <View style={styles.titleContainer}>
                  <Text style={styles.exerciseName}>
                    Alternative Exercise: {exercise.alternative_exercise}
                  </Text>
                  {exercise.alternative_exercise_media_url && (
                    <Image
                      source={{ uri: exercise.alternative_exercise_media_url }}
                      style={styles.thumbnail}
                      resizeMode="contain"
                    />
                  )}
                </View>
              </TouchableOpacity>

              {isAlternativeExpanded && (
                <View style={styles.alternativeDetails}>
                  {exercise.alternative_exercise_weight && (
                    <View style={styles.fieldRow}>
                      <Text style={styles.fieldLabel}>Weight:</Text>
                      <Text style={styles.fieldValue}>
                        {exercise.alternative_exercise_weight}
                      </Text>
                    </View>
                  )}

                  {exercise.alternative_exercise_reps && (
                    <View style={styles.fieldRow}>
                      <Text style={styles.fieldLabel}>Reps:</Text>
                      <Text style={styles.fieldValue}>
                        {exercise.alternative_exercise_reps}
                      </Text>
                    </View>
                  )}

                  {exercise.alternative_exercise_setup && (
                    <View style={styles.section}>
                      <Text style={styles.sectionTitle}>Setup:</Text>
                      <Text style={styles.sectionText}>
                        {exercise.alternative_exercise_setup}
                      </Text>
                    </View>
                  )}

                  {exercise.alternative_exercise_execution && (
                    <View style={styles.section}>
                      <Text style={styles.sectionTitle}>Execution:</Text>
                      {renderExecution(exercise.alternative_exercise_execution)}
                    </View>
                  )}
                </View>
              )}
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
    alignItems: "center",
    padding: 16,
    backgroundColor: "#f8f9fa",
    borderLeftWidth: 4,
    borderLeftColor: "#007AFF",
    borderRadius: 8,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  headerExpanded: {
    backgroundColor: "#e8f4f8",
    borderLeftColor: "#0051D5",
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
    fontSize: 18,
    color: "#007AFF",
    fontWeight: "bold",
    marginLeft: 12,
    paddingLeft: 8,
  },
  details: {
    padding: 16,
    backgroundColor: "#ffffff",
  },
  fieldRow: {
    flexDirection: "row",
    marginBottom: 8,
    alignItems: "flex-start",
  },
  fieldLabel: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#333333",
    marginRight: 8,
  },
  fieldValue: {
    fontSize: 14,
    color: "#666666",
    flex: 1,
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
  executionStep: {
    fontSize: 14,
    color: "#666666",
    lineHeight: 25,
    marginTop: 4,
    marginBottom: 4,
  },
  alternativeContainer: {
    marginTop: 12,
    backgroundColor: "#f0f0f0",
    borderRadius: 8,
    overflow: "hidden",
  },
  alternativeHeader: {
    flexDirection: "row",
    alignItems: "center",
    padding: 16,
    backgroundColor: "#f0f0f0",
    borderLeftWidth: 4,
    borderLeftColor: "#6c757d",
    borderRadius: 8,
  },
  alternativeHeaderExpanded: {
    backgroundColor: "#e9ecef",
    borderLeftColor: "#495057",
  },
  alternativeDetails: {
    padding: 16,
    backgroundColor: "#ffffff",
  },
  tipsContainer: {
    marginTop: 13,
    padding: 15,
    backgroundColor: "#e8f4f8",
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#b3d9e6",
  },
  tipsText: {
    fontSize: 14,
    color: "#333333",
    lineHeight: 20,
  },
})

export default ExerciseCard
