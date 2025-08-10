import Constants from "expo-constants"

const apiFromConfig = (Constants.expoConfig?.extra as any)?.API_URL as
  | string
  | undefined

export const API_BASE =
  apiFromConfig ||
  (process.env.NODE_ENV === "development" ? "http://localhost:8000" : "")

if (!API_BASE) {
  // If this throws on Vercel, the var wasn’t available to the build
  throw new Error("EXPO_PUBLIC_API_URL is required for API base URL")
}
