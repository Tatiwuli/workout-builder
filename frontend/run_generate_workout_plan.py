from agents.build_workout_plan import WorkoutBuilderWorkflow
import streamlit as st



# # Initialize session state for progress container
# if "progress_container" not in st.session_state:
#     st.session_state["progress_container"] = st.empty()


# def update_progress(message, percentage):
    
#     with st.session_state["progress_container"].container():
#         st.info(message)
#         st.progress(percentage)


def trigger_generate_workout_plan():
    st.session_state["trigger_generate_plan"] = True


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


def generate_workout_plan(user_responses, progress_callback=None):
    """
    Generates the workout plan using the workflow.
    """
    processed_responses = process_user_responses(user_responses)
    workflow = WorkoutBuilderWorkflow(progress_callback=handle_progress)
    return workflow.run_workflow(processed_responses)


def run_generate_workout_plan():
    try:
        with st.spinner("Generating your workout plan..."):
            #trigger backend to generate workout plan 
            st.session_state["workout_plan"] = generate_workout_plan(
                st.session_state["responses"], progress_callback=handle_progress)
        st.session_state["trigger_generate_plan"] = False
        st.rerun() #rerun to remove the progress bars and render the workout plan 
    except Exception as e:
        st.error(f"Failed to generate workout plan: {e}")
        st.session_state["trigger_generate_plan"] = False

