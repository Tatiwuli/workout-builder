# API Configuration Guide

## Environment Variables

The API service now supports configuration via environment variables for better flexibility across different environments.

### Supported Environment Variables

```bash

EXPO_PUBLIC_API_URL=https://workout-builder-g4n6.onrender.com/

# # Legacy/alternative options
# REACT_APP_API_URL=http://localhost:8000
# API_URL=http://localhost:8000

# Retry Configuration
API_RETRY_COUNT=2        # Number of retry attempts
API_RETRY_DELAY=2000     # Delay between retries (milliseconds)
API_TIMEOUT=30000        # Request timeout (milliseconds)
```

### Environment Examples

#### Development (default)

```bash
EXPO_PUBLIC_API_URL=http://localhost:8000
API_RETRY_COUNT=2
API_RETRY_DELAY=2000
API_TIMEOUT=30000
```

#### Production (Vercel + Render)

- Set `EXPO_PUBLIC_API_URL` in your Vercel Project → Settings → Environment Variables
- Value should be your Render backend base URL, e.g. `https://your-api.onrender.com`

```bash
EXPO_PUBLIC_API_URL https://workout-builder-g4n6.onrender.com/
API_RETRY_COUNT=1
API_RETRY_DELAY=3000
API_TIMEOUT=60000
```

## Programmatic Configuration

You can also configure the API service programmatically:

```typescript
import { apiService } from "./src/services/api"

// Update configuration at runtime
apiService.updateConfig({
  baseUrl: "https://custom-api.com",
  retryCount: 3,
  retryDelay: 1000,
  timeout: 45000,
})

// Get current configuration
const config = apiService.getConfig()
console.log("Current API config:", config)
```

## New API Pattern

The API now follows the standard async/await pattern with exceptions:

### Before (Result Pattern)

```typescript
const result = await apiService.generateWorkoutPlan(data)
if (result.success) {
  // Use result.data
} else {
  // Handle result.error
}
```

### After (Exception Pattern)

```typescript
try {
  const workoutPlan = await apiService.generateWorkoutPlan(data)
  // Use workoutPlan directly
} catch (error) {
  // Handle error
  console.error("API call failed:", (error as Error).message)
}
```

## Health Check

You can verify connectivity using the built-in health check:

```typescript
const ok = await apiService.testConnection() // calls `${baseUrl}/health`
```

## Benefits

1. **Environment Flexibility**: Easy configuration for dev/staging/prod
2. **Clean Error Handling**: Standard try/catch pattern
3. **Configurable Retry Logic**: Adjust retry behavior per environment
4. **Backward Compatibility**: Legacy methods still work
5. **Type Safety**: Full TypeScript support with proper types
