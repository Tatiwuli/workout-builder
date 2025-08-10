// src/env.ts
const env = (typeof process !== "undefined" ? process.env : {}) as Record<
  string,
  string | undefined
>

// Prod: must be provided by Vercel at build time.
// Dev: fallback to localhost so you can run locally without Vercel.
export const API_BASE =
  env.EXPO_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "development" ? "http://localhost:8000" : "")

if (!API_BASE) {
  // If this throws on Vercel, the env var wasn't available to the build.
  throw new Error("EXPO_PUBLIC_API_URL is required for API base URL")
}
