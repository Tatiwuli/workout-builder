# 🔗 Backend Integration Guide

## ✅ **What's Been Implemented**

### **1. FastAPI Server (`api_server.py`)**

- REST API endpoints for React Native frontend
- Integration with existing AI workflow agents
- Real-time progress tracking for workout generation
- CORS enabled for cross-origin requests

### **2. Updated React Native Frontend**

- Real API calls instead of mock data
- Progress tracking during AI generation (2+ minutes)
- Error handling and retry mechanisms
- Enhanced loading states with progress bars

### **3. API Endpoints Available**

| Endpoint                            | Method | Description                 |
| ----------------------------------- | ------ | --------------------------- |
| `/`                                 | GET    | Health check                |
| `/muscle_groups`                    | GET    | Get available muscle groups |
| `/questionnaire_options`            | GET    | Get dropdown options        |
| `/generate_workout_plan`            | POST   | Generate AI workout plan    |
| `/generation_progress/{session_id}` | GET    | Get generation progress     |
| `/save_workout_plan`                | POST   | Save generated plan         |
| `/saved_workout_plans`              | GET    | Get saved plans             |

## 🚀 **How to Start**

```bash
cd workout-builder
pip install -r api_requirements.txt
python start_servers.py
```

## 🔄 **How It Works**

### **Workflow Integration**

1. **User completes questionnaire** in React Native app
2. **Frontend calls** `/generate_workout_plan` with user data
3. **FastAPI server** converts data and calls AI:
   - `ExerciseSelectorAgent`
   - `WorkoutPlannerAgent`
   - `PersonalTrainerAgent`
4. **Progress updates** sent via `/generation_progress/{session_id}`
5. **Generated plan** returned to React Native app
6. **User sees** personalized AI-generated workout

### **Data Flow**

```
React Native → FastAPI → AI Agents → JSON Files
     ↑                                    ↓
     ←── Real-time Progress Updates ←─────┘
```


## 🔧 **Configuration**

### **API Server Settings**

- **Port**: 8000 (configurable in `api_server.py`)
- **CORS**: Enabled for all origins (change for production)
- **Data Storage**: JSON files (same as current system)

### **React Native Settings**

- **API Base URL**: `http://localhost:8000` (in `src/services/api.ts`)
- **Progress Polling**: Every 2 seconds
- **Timeout**: No timeout (generation can take 2+ minutes)
