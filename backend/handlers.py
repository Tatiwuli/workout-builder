
import streamlit as st 
from agents.build_workout_plan import WorkoutBuilderWorkflow


def process_user_responses(user_responses):
    """
    Processes raw user responses to prepare them for the workflow.
    """
    workout_duration = user_responses.get("workout_duration", 0)
    if workout_duration < 45:
        user_responses["time_range"] = "short"
    elif 45 <= workout_duration <= 60:
        user_responses["time_range"] = "mid"
    else:
        user_responses["time_range"] = "long"

    experience_mapping = {
        "I'm just starting out and have less than 3 months of experience.": "Beginner",
        "I’ve been consistently training for 3 months to 1 year.": "Intermediate",
    }
    user_responses["experience_level"] = experience_mapping.get(
        user_responses.get("experience_level"), "Unknown"
    )
    return user_responses


def handle_progress(message, percentage):
    """
    Sends progress updates to the frontend.
    """
    
    st.info(message)
    st.progress(percentage)


def generate_workout_plan(user_responses, progress_callback = None):
    """
    Generates the workout plan using the workflow.
    """
    processed_responses = process_user_responses(user_responses)
    workflow = WorkoutBuilderWorkflow(progress_callback=handle_progress)
    return workflow.run_workflow(processed_responses)
