# 📌 Table of Contents

1. [Project Overview](#project-overview)
2. [App Overview](#app-overview)
3. [Codebase Overview](#codebase-overview)
   - [Backend Overview](#1-backend-overview)
      - [Data Preparation](#1-data-preparation-backendscriptsdata_preparation)
      - [Workout Plan Workflow](#2-workout-plan-workflow)
         - [Optimize the Workout Plan Generation Duration](https://github.com/Tatiwuli/workout-builder/blob/main/README.md#-speeding-up-the-workout-plan-generation-from-5-to-2-minutes)
   - [Tech Stack](#tech-stack)
4. [Next Steps](#next-steps)
5. [Important Notes](#important-notes)
---

# 🗺️Project Overview

#### Access the website through this link: https://workout-builder-one.vercel.app/

This project generates customized workout plans tailored to user needs and hypertrophy goals. It manages the entire workflow: from selecting exercises and designing workout volume to structuring easy-to-follow workout plans through specialized agents.

### Purpose

I started my fitness journey five years ago, making a lot of mistakes, such as misunderstanding that weightlifting would make me bulkier, cardio would make me leaner, and **wasting time on trendy but ineffective exercises.**

Things started to change when I discovered YouTubers like Jeff Nippard and Dr. Mike, where I learned how fat loss and muscle building actually work, and developed a healthier mindset toward weightlifting.

Today, fitness is a daily habit that boosts my energy and confidence. As a student, hiring a personal trainer isn’t affordable, so I learned how to create my own workout plans by watching these YouTube channels. Over time, I saw significant improvements in my strength and physique. However, the process wasn’t the most efficient. On average, I spent 1–2 hours each week watching videos, taking notes, and connecting the insights to learn how to build my workout plans.

**To streamline this process, I decided to create a web app that references credible, science-based videos to build effective workout plans. This app learns about users' needs and preferences to generate plans tailored to their goals, making the process of structuring a workout session less stressful and more efficient.**

---

# APP OVERVIEW

## 📃Pages

### Home

Welcome page with a short description about the web app and a button to Generate Workout Plan

### Questionnaire

Interactive questionnaire that collects your workout needs and preferences. This information guides the agents to create a personalized workout plan.

<img src="https://github.com/Tatiwuli/workout-builder/blob/main/demo-home-questionnaire.gif" width="500">

### Workout Plan

The customized workout plan has two main sections:

- **Warmup**: Dynamic movements with execution notes, sets/reps, and duration
- **Main Workout**: Exercise sets organized by muscle groups (may include supersets or drop sets based on your goals). Each exercise includes step-by-step instructions with GIFs, recommended weights/sets/reps, and an alternative exercise.

<img src="https://github.com/Tatiwuli/workout-builder/blob/main/demo-workoutPlan.gif" width="500">

---

# 👩‍💻 Codebase Overview

## 1. Backend Overview

The backend splits into two core steps:

1. Preparing the fitness knowledge base
2. Running a multi-step workflow with Gemini models (OpenAI as fallback) to generate personalized workout plans.

## 1. Data Preparation: `backend/scripts/data_preparation/`

The goal here was to turn long-form YouTube content into structured documents to facilitate data retrieval. The pipeline works like this:

1. **Fetch transcripts**: Use the YouTube API to pull video metadata and transcripts.
2. **Summarize with an LLM**: Feed transcripts into an LLM to extract insights and structure them into JSON as instructed in `prompts.py`.
   (Learn more about how the LLM structures transcripts in 1.1 “How I designed the data schema.”)
3. **Store data in MongoDB**: The summaries are stored in MongoDB. See related files: `mongodb_handler.py`, `save_video_data.py`.

The workflow lives in `run_data_preparation.py`.

### 1.1 How I designed the data schema

To design the schemas from scratch, I asked myself: if I'm an LLM trainer who is smart but with zero domain knowledge, what would I need to build a workout plan based on the instructions I'd receive? I also take into consideration on how to make the data retrieval process on runtime as intuitive as possible.

For example, the exercise selector agent needs access to a list of exercises, an understanding of each exercise’s role, and execution details. Hence, it can select exercises that meet the user’s goals. At the same time, other agents need overall training principles for each muscle group to plan the other parts of the workout. Therefore, I split the videos into two data: exercises_summary(compact exercise-level records used by the selector) and main_knowledge_summaries (defining the `muscle_groups` as the dictionaire's key, and the additional informations of each muscle group as the corresponding values).

By designing the schema around what the agents actually consume, we make sure the LLMs focus on the most relevant content in the videos. Otherwise, every time we generate a workout plan, they would need to re-read transcripts and extract the same information for each user. Our approach allows the codebase to programmatically fetch the specific, relevant parts of the videos and feed only those to the LLMs. The data retrieval logic is in `build_workout_plan.py`.

---

## 2. Workout Plan Workflow

The runtime pipeline takes user inputs, retrieves knowledge from MongoDB, runs three agents in sequence, then programmatically compiles everything into a single strict plan object for the frontend.

### The three-agent workflow

The orchestration happens in `backend/app/agents/build_workout_plan.py`. Here's the flow:

1. **Fetch knowledge**: Pull `exercises_summary`, `main_knowledge_summaries`, and relevant wikis based on the user's muscle groups and fitness level.
2. **Exercise Selector** (`backend/app/agents/exercise_selector_agent.py`):
   - Chooses exercises that match the user's goals, fitness level, and time constraints.
   - Writes client-friendly setup and execution instructions.
   - **Input**: user needs + `exercises_summary` + shared context (wikis + principles).
   - **Output**: a list of exercises with name, setup, execution, targets, alternatives, and notes.

3. **Workout Planner** (`backend/app/agents/workout_planner_agent.py`):
   - Defines the volume (sets and reps) and the duration of each selected exercise.
   - **Input**: selected exercises + workout duration
   - **Output**: an array of `sets`, each containing exercises with reps, weight, and rest periods.

4. **Warmup Agent** (`backend/app/agents/warmup_agent.py`):
   - Builds a warmup section that's consistent with the main workout.
   - **Input**: the compiled plan (without warmup).
   - **Output**: a warmup block with duration and exercises.

The agents’ outputs are compiled programmatically to avoid unnecessary latency from making another LLM request just to compile. The compiler in `build_workout_plan.py` takes the selector's exercises and the planner's sets, normalizes fields like `setup` and `execution` into lists, and merges everything into one plan. This keeps the frontend schema predictable and reduces parsing errors.

### The LLM models:

Both agents call a common `LLMService` (see `backend/app/llms/llm_model.py`) that tries Gemini with exponential backoff retries, then falls back to OpenAI if Gemini exhausts its attempts. The service supports both streaming and non-streaming modes, and both providers use structured output to enforce JSON schemas.

The actual LLM clients live in `backend/app/llms/llm.py`: `GeminiLLM` uses Google's `genai` SDK with dynamic thinking budgets, and `OpenAILLM` uses OpenAI's Responses API with prompt caching.

---

### ⏩ Speeding up the workout plan generation from 5 to <2 minutes:

<img src="https://github.com/Tatiwuli/workout-builder/blob/main/GenerationTimeInfograph.png" width="500">

The agents workflow was iterated extensively to optimize performance. Here's a breakdown of the key optimizations:

#### Optimization 1: Consolidate database calls (5 min → 2 min)

**Before:** Each agent independently fetched the data it needed from MongoDB, resulting in 3 separate database calls for 3 agents.

**After:** Created a single `fetch_workout_plan` function that retrieves all necessary data from MongoDB once and stores it in a local dictionary, sharing th data across all agents.

#### Optimization 2: Minimize data passed between agents

**Before:** The workout planner received the full exercise summaries from the selector to reference when setting volume for each exercise.

**After:** Replaced the entire summary document with a single `additional_notes` field containing only the relevant insights for each selected exercise, written by the exercise selector. This significantly reduced the context size for the planner.

#### Optimization 3: Improve the prompt engineering

**Before:** Prompts were lengthy and contained redundant instructions.

**After:** Specified the task and step-by-step process directly in the prompt. Removed instructions that could be inferred from the context (passed wikis). Focused the prompts on explaining how agents should use the provided context and what they need to generate.

#### Optimization 4: Implement prompt caching (2 min → <2 min)

**Challenge:** Gemini offered faster inference but occasionally returned service errors, requiring fallback to OpenAI. However, OpenAI has a slower performance than Gemini.

**Solution:** I used the prefix technique to trigger OpenAI's built-in prompt caching mechanism, which significantly sped up inference on fallback requests.

#### Optimization 5: Enforce structured outputs with Pydantic

Before, Gemini occasionally returned malformed JSON, wasting time on invalid outputs.
To solve this, I integrated Pydantic models and used structured response schemas to validate outputs before processing, eliminating time spent waiting for invalid JSON responses.

## 🧰Tech Stack

### Backend

- Python (FastAPI)

### Frontend

- React Native (Type Script)

React Native was chosen to maintain the flexibility for evolving the app into a mobile app.

### APIs

**Backend and Frontend Communication**

The app uses an **HTTP API** built with FastAPI that implements an asynchronous polling pattern to handle long-running workout generation:

1. **POST `/generate_workout_plan`**: Frontend submits user responses and receives a `session_id`.
2. **GET `/generation_progress/{session_id}`**: Frontend polls every 3 seconds to track progress (0-100%), status (`running`, `completed`, `error`), and receive real-time messages.
3. **GET `/get_final_plan/{session_id}`**: Retrieves the complete workout plan once generation is finished.

All responses follow a consistent structure: `{ success: boolean, data: {...}, error?: string }`. The frontend uses a custom `useWorkoutPolling` hook to manage the polling lifecycle and handle edge cases (network failures, retries, component unmounting).

**Third Party Services**

- **YouTube API:** Fetches videos from specific playlists.
- **Gemini API, OpenAI API:** Access the LLM models

---

# 🏃‍♀️Next Steps

While the workout plans follow principles from credible hypertrophy experts, the fitness knowledge base is constrained by the structure of the source videos.I'm exploring ways to make the LLM system reason more independently through science-based exercise principles, including: Fine-tuning domain-specific models; Implementing more advanced agentic systems

Based on user feedback, the app will expand to include more calisthenics and minimal-equipment workouts while maintaining effective strength training and muscle development principles.

# Important Notes

- Disclaimer: These workout plans are not designed by a professional. Please review them carefully, and if you have any injuries, consult a professional before proceeding.
- Content Sources: The exercises and volume design principles are inspired by the following credible YouTube channels:
  - Renaissance Periodization
  - Jeff Nippard
