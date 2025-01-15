
import streamlit as st
from dotenv import load_dotenv
import os

from agents.build_workout_plan import WorkoutBuilderWorkflow
from streamlit_cookies_manager import EncryptedCookieManager


def trigger_generate_workout_plan():
    """
    Update the session state to trigger workout plan generation stage
    """
    st.session_state["trigger_generate_plan"] = True


def process_user_responses(user_responses):
    """
    Processes raw user responses to  pass to  agents
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


def generate_workout_plan(user_api_key, user_responses, progress_callback=None):
    """
    Generates the workout plan with agents
    """
    # process user responses
    processed_responses = process_user_responses(user_responses)
    # trigger agents to start the building process
    workflow = WorkoutBuilderWorkflow(
        progress_callback=handle_progress, api_key=user_api_key)
    return workflow.run_workflow(processed_responses)


def run_generate_workout_plan():
    load_dotenv()
    COOKIE_PASSWORD =  st.secrets.get(
        "COOKIE_PASSWORD") or os.getenv("COOKIE_PASSWORD")

    cookies = EncryptedCookieManager(
        prefix="workout_builder_", password=COOKIE_PASSWORD)  # expires after 30 minutes
    if not cookies.ready():
        st.stop()

    # Retrieve the API key
    user_api_key = cookies.get("api_key", None)
    print(user_api_key)

    try:
        with st.spinner("Generating your workout plan..."):
            # trigger backend to generate workout plan
            st.session_state["workout_plan"] = generate_workout_plan(
                user_api_key, st.session_state["responses"], progress_callback=handle_progress)

        st.session_state["trigger_generate_plan"] = False

        # rerun to remove the progress bars and render the workout plan
        st.rerun()
    except Exception as e:
        st.error(f"Failed to generate workout plan: {e}")
        st.session_state["trigger_generate_plan"] = False
