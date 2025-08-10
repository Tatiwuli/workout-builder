import React, { useEffect } from "react"
import { NavigationContainer } from "@react-navigation/native"
import { createStackNavigator } from "@react-navigation/stack"
import { StatusBar } from "expo-status-bar"
import { SafeAreaProvider } from "react-native-safe-area-context"
import { Platform } from "react-native"
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
    // Simple health check on startup
    apiService
      .testConnection()
      .then((ok) => console.log("API health:", ok ? "OK" : "DOWN"))
      .catch(() => console.log("API health: DOWN"))

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
