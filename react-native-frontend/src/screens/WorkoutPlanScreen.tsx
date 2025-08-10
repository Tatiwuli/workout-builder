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

// Mock workout plan data - replace with actual API call
const mockWorkoutPlan: WorkoutPlan = {
  workout_title: "(MOCK WORKOUT PLAN)Upper Body Strength & Hypertrophy",
  total_workout_duration: "60 minutes",
  num_exercises: 8,
  warmup: {
    warmup_duration: "10 minutes",
    warmup_exercises: [
      {
        exercise_name: "Arm Circles",
        setup: "Stand with feet shoulder-width apart, arms extended to sides",
        execution:
          "Make small circular motions with arms, gradually increasing size. 10 forward, 10 backward.",
      },
      {
        exercise_name: "Light Push-ups",
        setup:
          "Start in plank position with hands slightly wider than shoulders",
        execution: "Perform 5-10 light push-ups to warm up chest and triceps.",
      },
    ],
  },
  sets: [
    {
      set_number: 1,
      target_muscle_group: ["Chest", "Triceps"],
      exercises: [
        {
          exercise_name: "Barbell Bench Press",
          setup:
            "Lie on bench with feet flat on ground, grip slightly wider than shoulder width",
          execution:
            "Lower bar to chest, press up explosively. 3 sets of 8-10 reps.",
        },
        {
          exercise_name: "Incline Dumbbell Press",
          setup:
            "Set bench to 30-45 degree incline, hold dumbbells at shoulder level",
          execution:
            "Press dumbbells up and together, control descent. 3 sets of 10-12 reps.",
        },
      ],
    },
    {
      set_number: 2,
      target_muscle_group: ["Back", "Biceps"],
      exercises: [
        {
          exercise_name: "Pull-ups",
          setup: "Grip pull-up bar with hands slightly wider than shoulders",
          execution:
            "Pull body up until chin clears bar, control descent. 3 sets of 6-8 reps.",
        },
        {
          exercise_name: "Bent-over Rows",
          setup:
            "Stand with feet shoulder-width, bend at hips, hold barbell with overhand grip",
          execution:
            "Pull bar to lower chest, squeeze shoulder blades. 3 sets of 10-12 reps.",
        },
      ],
    },
  ],
}

const formatDuration = (duration: string) => {
  // const [hours, minutes] = duration.split(" ").map(Number)
  // if (hours > 0) {
  //   return `${hours}h ${minutes}m`
  // }
  // If it's already a string like "60 minutes" just return it or strip words
  const numeric = parseFloat(duration)
  if (!isNaN(numeric)) {
    return `${Math.round(numeric)} min`
  }
  return duration
}

const WorkoutPlanScreen: React.FC<Props> = ({ navigation, route }) => {
  const [expandedExercises, setExpandedExercises] = useState<Set<string>>(
    new Set()
  )

  // Get workout plan from navigation params or use mock data as fallback
  const workoutPlan: WorkoutPlan = route.params?.workoutPlan || mockWorkoutPlan

  // Debug log to see what we received
  console.log("WorkoutPlanScreen received data:", route.params)
  console.log("Using workout plan:", workoutPlan)

  const toggleExercise = (exerciseName: string) => {
    const newExpanded = new Set(expandedExercises)
    if (newExpanded.has(exerciseName)) {
      newExpanded.delete(exerciseName)
    } else {
      newExpanded.add(exerciseName)
    }
    setExpandedExercises(newExpanded)
  }

  const renderWarmupSection = () => (
    <View style={styles.section}>
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>🔥 Warm-Up</Text>
        <Text style={styles.sectionDuration}>
          {formatDuration(workoutPlan.warmup.warmup_duration)}
        </Text>
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

  const renderWorkoutSets = () => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>💪 Workout Sets</Text>

      {workoutPlan.sets.map((set, setIndex) => (
        <View key={setIndex} style={styles.setContainer}>
          <View style={styles.setHeader}>
            <Text style={styles.setNumber}>Set {set.set_number}</Text>
            <Text style={styles.targetMuscles}>
              Target: {set.target_muscle_group.join(", ")}
            </Text>
          </View>

          {set.exercises.map((exercise, exerciseIndex) => (
            <ExerciseCard
              key={`set-${setIndex}-exercise-${exerciseIndex}`}
              exercise={exercise}
              isExpanded={expandedExercises.has(exercise.exercise_name)}
              onToggle={() => toggleExercise(exercise.exercise_name)}
            />
          ))}
        </View>
      ))}
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
                  {formatDuration(workoutPlan.total_workout_duration)}
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
    marginBottom: 24,
  },
  setHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
    paddingHorizontal: 8,
  },
  setNumber: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#007AFF",
  },
  targetMuscles: {
    fontSize: 14,
    color: "#666666",
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
