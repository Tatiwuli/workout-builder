import React, { useEffect } from "react"
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
  Alert,
} from "react-native"
import { StackNavigationProp } from "@react-navigation/stack"
import { RouteProp } from "@react-navigation/native"
import { RootStackParamList } from "../../App"
import { useWorkoutPolling } from "../hooks"

type WorkoutGenerationScreenNavigationProp = StackNavigationProp<
  RootStackParamList,
  "WorkoutGeneration"
>

type WorkoutGenerationScreenRouteProp = RouteProp<
  RootStackParamList,
  "WorkoutGeneration"
>

interface Props {
  navigation: WorkoutGenerationScreenNavigationProp
  route: WorkoutGenerationScreenRouteProp
}

const WorkoutGenerationScreen: React.FC<Props> = ({ navigation, route }) => {
  const { sessionId } = route.params
  const { isLoading, error, workoutPlan, retry } = useWorkoutPolling(sessionId)

  // Auto-navigate to WorkoutPlan when generation completes
  useEffect(() => {
    if (workoutPlan) {
      console.log("Workout generation completed, navigating to WorkoutPlan")
      navigation.replace("WorkoutPlan", { workoutPlan })
    }
  }, [workoutPlan, navigation])

  // Rotating through these messages
  const loadingMessages = [
    "🤖 Our AI is crafting your perfect workout... This usually takes 1-2 minutes! ⏳",
    "💪 Analyzing your goals and building something amazing...",
    "🔥 Selecting the best exercises just for you...",
    "⚡ Almost there! Creating your personalized plan...",
    "🎯 Fine-tuning your workout for maximum results...",
  ]

  const [currentMessageIndex, setCurrentMessageIndex] = React.useState(0)

  // Rotate loading messages every 10 seconds
  useEffect(() => {
    if (!isLoading) return

    const interval = setInterval(() => {
      setCurrentMessageIndex((prev) => (prev + 1) % loadingMessages.length)
    }, 8000)

    return () => clearInterval(interval)
  }, [isLoading, loadingMessages.length])

  const handleRetry = () => {
    // Use the hook's retry function to re-poll from same screen
    retry()
  }

  const handleGoHome = () => {
    navigation.navigate("Home")
  }

  if (error) {
    return (
      <View style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorIcon}>⚠️</Text>
          <Text style={styles.errorTitle}>Generation Failed</Text>
          <Text style={styles.errorMessage}>
            We couldn't generate your plan due to a server issue. Please try
            again - your form data is saved.
          </Text>
          {/* Retry Button */}
          <View style={styles.buttonContainer}>
            <TouchableOpacity
              style={styles.retryButton}
              onPress={handleRetry}
              activeOpacity={0.8}
            >
              <Text style={styles.retryButtonText}>Try Again</Text>
            </TouchableOpacity>
            {/* Home Button */}
            <TouchableOpacity
              style={styles.homeButton}
              onPress={handleGoHome}
              activeOpacity={0.8}
            >
              <Text style={styles.homeButtonText}>Back to Home</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    )
  }
  //if  no error, return loading screen
  return (
    <View style={styles.container}>
      <View style={styles.loadingContainer}>
        {/* AI Icon with Spinner */}
        <View style={styles.aiIconContainer}>
          <Text style={styles.aiIcon}>🤖</Text>
          <ActivityIndicator
            size="large"
            color="#007AFF"
            style={styles.spinner}
          />
        </View>

        {/* Title */}
        <Text style={styles.loadingTitle}>AI Workout Generation</Text>

        {/* Fun rotating message */}
        <Text style={styles.loadingMessage}>
          {loadingMessages[currentMessageIndex]}
        </Text>

        {/* Progress indicator */}
        <View style={styles.progressSection}>
          <View style={styles.progressDots}>
            {[0, 1, 2].map((index) => (
              <View
                key={index}
                style={[
                  styles.progressDot,
                  {
                    opacity: currentMessageIndex % 3 >= index ? 1 : 0.3,
                  },
                ]}
              />
            ))}
          </View>
          <Text style={styles.progressText}>
            Hang tight, we're building the plan to build your body 😎
          </Text>
        </View>

        {/* Back button for impatient users */}
        <TouchableOpacity
          style={styles.backButton}
          onPress={handleGoHome}
          activeOpacity={0.8}
        >
          <Text style={styles.backButtonText}>← Back to Home</Text>
        </TouchableOpacity>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#ffffff",
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  loadingContainer: {
    alignItems: "center",
    padding: 20,
    backgroundColor: "#f8f9fa",
    borderRadius: 16,
    maxWidth: 350,
    width: "100%",
  },
  aiIconContainer: {
    position: "relative",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 20,
  },
  aiIcon: {
    fontSize: 64,
    marginBottom: 10,
  },
  spinner: {
    position: "absolute",
    top: 30,
  },
  loadingTitle: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#333333",
    marginBottom: 16,
    textAlign: "center",
  },
  loadingMessage: {
    fontSize: 16,
    color: "#007AFF",
    fontWeight: "600",
    marginBottom: 30,
    textAlign: "center",
    lineHeight: 24,
    minHeight: 48, // Prevent layout shift when message changes
  },
  progressSection: {
    alignItems: "center",
    marginBottom: 30,
  },
  progressDots: {
    flexDirection: "row",
    marginBottom: 12,
  },
  progressDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: "#007AFF",
    marginHorizontal: 4,
  },
  progressText: {
    fontSize: 14,
    color: "#666666",
    textAlign: "center",
    fontStyle: "italic",
  },
  backButton: {
    backgroundColor: "#e9ecef",
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
  },
  backButtonText: {
    color: "#666666",
    fontSize: 14,
    fontWeight: "500",
  },
  // Error state styles
  errorContainer: {
    alignItems: "center",
    padding: 20,
    backgroundColor: "#fff5f5",
    borderRadius: 16,
    borderWidth: 1,
    borderColor: "#fed7d7",
    maxWidth: 350,
    width: "100%",
  },
  errorIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  errorTitle: {
    fontSize: 22,
    fontWeight: "bold",
    color: "#e53e3e",
    marginBottom: 12,
    textAlign: "center",
  },
  errorMessage: {
    fontSize: 16,
    color: "#666666",
    textAlign: "center",
    lineHeight: 24,
    marginBottom: 30,
  },
  buttonContainer: {
    width: "100%",
    gap: 12,
  },
  retryButton: {
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
  retryButtonText: {
    color: "#ffffff",
    fontSize: 18,
    fontWeight: "bold",
  },
  homeButton: {
    backgroundColor: "#f8f9fa",
    paddingVertical: 15,
    borderRadius: 25,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#dee2e6",
  },
  homeButtonText: {
    color: "#666666",
    fontSize: 16,
    fontWeight: "600",
  },
})

export default WorkoutGenerationScreen
