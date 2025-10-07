import React, { useEffect } from "react"
import { NavigationContainer } from "@react-navigation/native"
import { createStackNavigator } from "@react-navigation/stack"
import { StatusBar } from "expo-status-bar"
import { SafeAreaProvider } from "react-native-safe-area-context"
import { Platform } from "react-native"
import { API_BASE } from "./src/env"
import { apiService } from "./src/services/api"

import HomeScreen from "./src/screens/HomeScreen"
import QuestionnaireScreen from "./src/screens/QuestionnaireScreen"
import WorkoutGenerationScreen from "./src/screens/WorkoutGenerationScreen"
import WorkoutPlanScreen from "./src/screens/WorkoutPlanScreen"

export type RootStackParamList = {
  Home: undefined
  Questionnaire: undefined
  WorkoutGeneration: { sessionId: string }
  WorkoutPlan: { workoutPlan: any }
}

const Stack = createStackNavigator<RootStackParamList>()

export default function App() {
  useEffect(() => {
    // Enhanced API ping on startup to warm up connection
    const pingApi = async () => {
      console.log("🏋️‍♂️ Workout Builder starting up...")
      console.log("API base:", API_BASE)

      try {
        // Use the API service with retry logic for the startup ping
        const isConnected = await apiService.testConnection()
        console.log(
          "✅ API health check successful:",
          isConnected ? "Connected" : "Failed"
        )
      } catch (error) {
        console.warn("⚠️ API health check failed:", error)
        // Don't throw error here as it's just a warm-up ping
        // The app should still work even if the initial ping fails
      }
    }

    // Execute the ping immediately when app starts
    pingApi()

    if (Platform.OS === "web") {
      // Inject CSS for web platform
      const style = document.createElement("style")
      style.textContent = `
        html, body {
          height: 100%;
          overflow: auto;
          -webkit-overflow-scrolling: touch;
          overscroll-behavior: auto;
          margin: 0;
          padding: 0;
        }
        #root {
          height: 100vh;
          overflow: hidden;
        }
        [data-class*="ScrollView"] {
          overflow: auto !important;
          -webkit-overflow-scrolling: touch !important;
        }
      `
      document.head.appendChild(style)
    }
  }, [])

  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName="Home"
          screenOptions={{
            headerStyle: {
              backgroundColor: "#ffffff",
            },
            headerTintColor: "#007AFF",
            headerTitleStyle: {
              fontWeight: "bold",
              color: "#333333",
            },
            cardStyle: { flex: 1 },
          }}
        >
          <Stack.Screen
            name="Home"
            component={HomeScreen}
            options={{ title: "🏋️‍♂️ Workout Builder" }}
          />
          <Stack.Screen
            name="Questionnaire"
            component={QuestionnaireScreen}
            options={{ title: "📝 Questionnaire" }}
          />
          <Stack.Screen
            name="WorkoutGeneration"
            component={WorkoutGenerationScreen}
            options={{ title: "🤖 Generating Workout" }}
          />
          <Stack.Screen
            name="WorkoutPlan"
            component={WorkoutPlanScreen}
            options={{ title: "💪 Workout Plan" }}
          />
        </Stack.Navigator>
        <StatusBar style="dark" />
      </NavigationContainer>
    </SafeAreaProvider>
  )
}
