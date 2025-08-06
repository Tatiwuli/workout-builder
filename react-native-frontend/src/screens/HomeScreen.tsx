import React from "react"
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Dimensions,
  Platform,
} from "react-native"
import { SafeAreaView } from "react-native-safe-area-context"
import { StackNavigationProp } from "@react-navigation/stack"
import { RootStackParamList } from "../../App"

type HomeScreenNavigationProp = StackNavigationProp<RootStackParamList, "Home">

interface Props {
  navigation: HomeScreenNavigationProp
}

const { width } = Dimensions.get("window")

const HomeScreen: React.FC<Props> = ({ navigation }) => {
  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.contentContainer}
        showsVerticalScrollIndicator={true}
        scrollEnabled={true}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.content}>
          <Text style={styles.title}>🏋️‍♂️ Personalized Workout Builder</Text>

          <View style={styles.descriptionContainer}>
            <Text style={styles.description}>
              Create personalized, science-backed workout plans tailored to your
              goals.
            </Text>

            <Text style={styles.subDescription}>
              This app uses advanced AI trained on insights from:
            </Text>

            <View style={styles.bulletPoints}>
              <Text style={styles.bulletPoint}>
                🎓 Jeff Nippard's research-driven programs
              </Text>
              <Text style={styles.bulletPoint}>
                🧠 Dr. Mike Israetel & Renaissance Periodization's hypertrophy
                principles
              </Text>
            </View>

            <Text style={styles.finalDescription}>
              Whether you're just starting out or optimizing your next phase,
              we've got you covered.
            </Text>
          </View>

          <View style={styles.readySection}>
            <Text style={styles.readyTitle}>Ready to build your plan?</Text>

            <TouchableOpacity
              style={styles.button}
              onPress={() => navigation.navigate("Questionnaire")}
              activeOpacity={0.8}
            >
              <Text style={styles.buttonText}>📝 Start Questionnaire</Text>
            </TouchableOpacity>
          </View>
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
  contentContainer: {
    flexGrow: 1,
    paddingBottom: 40,
  },
  content: {
    padding: 20,
    paddingTop: 40,
  },
  title: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#333333",
    textAlign: "center",
    marginBottom: 30,
  },
  descriptionContainer: {
    marginBottom: 40,
  },
  description: {
    fontSize: 18,
    color: "#333333",
    textAlign: "center",
    marginBottom: 20,
    lineHeight: 26,
  },
  subDescription: {
    fontSize: 16,
    color: "#666666",
    textAlign: "center",
    marginBottom: 15,
  },
  bulletPoints: {
    marginBottom: 20,
    alignItems: "center",
  },
  bulletPoint: {
    fontSize: 16,
    color: "#333333",
    marginBottom: 8,
  },
  finalDescription: {
    fontSize: 16,
    color: "#666666",
    textAlign: "center",
    lineHeight: 24,
  },
  readySection: {
    alignItems: "center",
    marginTop: 20,
  },
  readyTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#333333",
    marginBottom: 20,
  },
  button: {
    backgroundColor: "#007AFF",
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
    minWidth: width * 0.7,
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

export default HomeScreen
