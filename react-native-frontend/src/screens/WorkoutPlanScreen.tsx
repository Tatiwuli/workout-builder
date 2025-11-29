import React, { useState } from "react"
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Platform,
} from "react-native"
import { SafeAreaView } from "react-native-safe-area-context"
import { StackNavigationProp } from "@react-navigation/stack"
import { RouteProp } from "@react-navigation/native"

import { RootStackParamList } from "../../App"
import { WorkoutPlan, Exercise } from "../types"
import ExerciseCard from "../components/ExerciseCard"

type WorkoutPlanScreenNavigationProp = StackNavigationProp<
  RootStackParamList,
  "WorkoutPlan"
>

type WorkoutPlanScreenRouteProp = RouteProp<RootStackParamList, "WorkoutPlan">

interface Props {
  navigation: WorkoutPlanScreenNavigationProp
  route: WorkoutPlanScreenRouteProp
}

// Convert float minutes, 'MM:SS' string, or 'HH:MM:SS' string to 'MM:SS' format string
const formatDurationToMMSS = (duration: number | string): string => {
  // If it's already a string, check for different formats
  if (typeof duration === "string") {
    const trimmed = duration.trim()

    // Check for 'HH:MM:SS' format (e.g., "00:15:00" or "01:30:45")
    const hmsPattern = /^(\d{1,2}):(\d{2}):(\d{2})$/
    const hmsMatch = trimmed.match(hmsPattern)
    if (hmsMatch) {
      const hours = parseInt(hmsMatch[1], 10)
      const minutes = parseInt(hmsMatch[2], 10)
      const seconds = parseInt(hmsMatch[3], 10)
      const totalMinutes = hours * 60 + minutes + seconds / 60
      // Convert to MM:SS format
      const totalSeconds = Math.round(totalMinutes * 60)
      const mins = Math.floor(totalSeconds / 60)
      const secs = totalSeconds % 60
      return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
    }

    // Check for 'MM:SS' format, return as-is
    const mmssPattern = /^\d{2}:\d{2}$/
    if (mmssPattern.test(trimmed)) {
      return trimmed
    }

    // Try to parse as float (in case it's a string representation of a number)
    const parsed = parseFloat(trimmed)
    if (!isNaN(parsed)) {
      duration = parsed
    } else {
      return "00:00" // Invalid format, return default
    }
  }

  // If it's a number (float minutes), convert to 'MM:SS'
  if (typeof duration === "number") {
    const totalSeconds = Math.round(duration * 60)
    const mins = Math.floor(totalSeconds / 60)
    const secs = totalSeconds % 60
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
  }

  return "00:00" // Fallback
}

const WorkoutPlanScreen: React.FC<Props> = ({ navigation, route }) => {
  const [expandedSets, setExpandedSets] = useState<Set<number>>(new Set())
  const [expandedExercises, setExpandedExercises] = useState<Set<string>>(
    new Set()
  )

  // Get workout plan from navigation params
  const workoutPlan: WorkoutPlan = route.params?.workoutPlan

  console.log("WorkoutPlanScreen received data:", route.params)
  console.log("Using workout plan:", workoutPlan)

  const toggleSet = (setNumber: number) => {
    const newExpanded = new Set(expandedSets)
    if (newExpanded.has(setNumber)) {
      newExpanded.delete(setNumber)
    } else {
      newExpanded.add(setNumber)
    }
    setExpandedSets(newExpanded)
  }

  const toggleExercise = (exerciseName: string) => {
    const newExpanded = new Set(expandedExercises)
    if (newExpanded.has(exerciseName)) {
      newExpanded.delete(exerciseName)
    } else {
      newExpanded.add(exerciseName)
    }
    setExpandedExercises(newExpanded)
  }

  const renderWarmupSection = () => {
    let warmupDuration = formatDurationToMMSS(
      workoutPlan.warmup.total_warmup_duration
    )

    // Default to 05:00 if duration is 00:00
    if (warmupDuration === "00:00") {
      warmupDuration = "05:00"
    }

    return (
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>🔥 Warm-Up</Text>
          <Text style={styles.sectionDuration}>⏱️ {warmupDuration}</Text>
        </View>

        {workoutPlan.warmup.warmup_exercises.map((exercise, index) => (
          <ExerciseCard
            key={`warmup-${index}`}
            exercise={exercise}
            isExpanded={expandedExercises.has(exercise.exercise_name)}
            onToggle={() => toggleExercise(exercise.exercise_name)}
          />
        ))}
      </View>
    )
  }

  const renderWorkoutSets = () => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>💪 Workout Sets</Text>

      {workoutPlan.sets.map((set, setIndex) => {
        const isSetExpanded = expandedSets.has(set.set_number)
        // const hasSetStrategy =
        //   set.set_strategy &&
        //   set.set_strategy.trim() !== "" &&
        //   set.set_strategy.toLowerCase() !== "none"

        return (
          <View key={setIndex} style={styles.setContainer}>
            <TouchableOpacity
              style={styles.setHeader}
              onPress={() => toggleSet(set.set_number)}
              activeOpacity={0.7}
            >
              <View style={styles.setHeaderLeft}>
                <Text style={styles.setNumber}>Set {set.set_number}</Text>
                <Text style={styles.setMetadata}>{set.num_rounds} rounds</Text>
                <Text style={styles.setMetadata}>
                  ⏱️ {formatDurationToMMSS(set.set_duration)}
                </Text>
                <Text style={styles.targetMuscles}>
                  💪Target Muscles: {set.target_muscle_group.join(", ")}
                </Text>
              </View>
              <View style={styles.setHeaderRight}>
                <Text style={styles.expandIcon}>
                  {isSetExpanded ? "▼" : "▶"}
                </Text>
              </View>
            </TouchableOpacity>

            {isSetExpanded && (
              <View style={styles.setContent}>
                {/* {hasSetStrategy && (
                  <Text style={styles.setStrategy}>{set.set_strategy}</Text>
                )} */}

                {set.exercises.map((exercise, exerciseIndex) => {
                  const exerciseKey = `set-${set.set_number}-exercise-${exerciseIndex}`
                  return (
                    <ExerciseCard
                      key={exerciseKey}
                      exercise={exercise}
                      isExpanded={expandedExercises.has(exercise.exercise_name)}
                      onToggle={() => toggleExercise(exercise.exercise_name)}
                    />
                  )
                })}
              </View>
            )}
          </View>
        )
      })}
    </View>
  )

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={true}
        bounces={false}
        scrollEnabled={true}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.content}>
          {/* Back to Home Button */}
          <TouchableOpacity
            style={styles.backHomeButton}
            onPress={() => navigation.navigate("Home")}
            activeOpacity={0.8}
          >
            <Text style={styles.backHomeText}>🏠 Back to Home</Text>
          </TouchableOpacity>

          <View style={styles.header}>
            <Text style={styles.title}>{workoutPlan.workout_title}</Text>
            <View style={styles.statsContainer}>
              <View style={styles.stat}>
                <Text style={styles.statLabel}>Duration</Text>
                <Text style={styles.statValue}>
                  ⏱️{" "}
                  {formatDurationToMMSS(
                    workoutPlan.total_workout_duration +
                      workoutPlan.warmup.total_warmup_duration
                  )}
                </Text>
              </View>
              <View style={styles.stat}>
                <Text style={styles.statLabel}>Exercises</Text>
                <Text style={styles.statValue}>
                  {typeof workoutPlan.num_exercises === "string"
                    ? workoutPlan.num_exercises
                    : workoutPlan.num_exercises}
                </Text>
              </View>
            </View>
          </View>

          <View style={styles.divider} />

          {renderWarmupSection()}

          <View style={styles.divider} />

          {renderWorkoutSets()}

          <View style={styles.divider} />
        </View>
      </ScrollView>
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
  },
  backHomeButton: {
    alignSelf: "flex-start",
    backgroundColor: "#f8f9fa",
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#dee2e6",
    marginBottom: 20,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  backHomeText: {
    color: "#666666",
    fontSize: 14,
    fontWeight: "600",
  },
  header: {
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#333333",
    textAlign: "center",
    marginBottom: 16,
  },
  statsContainer: {
    flexDirection: "row",
    justifyContent: "space-around",
  },
  stat: {
    alignItems: "center",
  },
  statLabel: {
    fontSize: 14,
    color: "#666666",
    marginBottom: 4,
  },
  statValue: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#007AFF",
  },
  divider: {
    height: 1,
    backgroundColor: "#e9ecef",
    marginVertical: 20,
  },
  section: {
    marginBottom: 20,
  },
  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#333333",
  },
  sectionDuration: {
    fontSize: 16,
    color: "#007AFF",
    fontWeight: "600",
  },
  setContainer: {
    marginBottom: 16,
    backgroundColor: "#f8f9fa",
    borderRadius: 8,
    overflow: "hidden",
  },
  setHeader: {
    flexDirection: "row",
    alignItems: "center",
    padding: 16,
    backgroundColor: "#ffffff",
  },
  setHeaderLeft: {
    flex: 1,
  },
  setNumber: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#333333",
    marginBottom: 4,
  },
  setMetadata: {
    fontSize: 14,
    color: "#666666",
    marginBottom: 2,
  },
  setHeaderRight: {
    flex: 1,
    alignItems: "flex-end",
    marginRight: 8,
  },
  targetMuscles: {
    fontSize: 14,
    color: "#666666",
    textAlign: "left",
  },
  expandIcon: {
    fontSize: 16,
    color: "#007AFF",
    fontWeight: "bold",
  },
  setContent: {
    padding: 16,
    backgroundColor: "#ffffff",
  },
  setStrategy: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#333333",
    marginBottom: 16,
  },
  footer: {
    marginTop: 30,
    alignItems: "center",
  },
  button: {
    backgroundColor: "#007AFF",
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
    minWidth: 200,
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
  buttonText: {
    color: "#ffffff",
    fontSize: 18,
    fontWeight: "bold",
  },
})

export default WorkoutPlanScreen
