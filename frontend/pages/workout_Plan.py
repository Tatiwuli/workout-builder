

import os
import streamlit as st
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit_nested_layout 

from frontend.run_generate_workout_plan import run_generate_workout_plan


st.set_page_config(page_title="Workout Plan", page_icon="💪")


def initialize_sessions_states():

    if "workout_plan" not in st.session_state:
        st.session_state["workout_plan"] = None


def render_media(media_url):
    """
    Function to render media based on the media_url.
    Supports GIFs and YouTube videos with specific start and end times.
    """
    if media_url:
        if media_url.endswith(".gif"):
            st.markdown(f"![Execution GIF]({media_url})")
        elif "youtube.com" in media_url:
            # Embed YouTube video with custom start and end times
            st.markdown(
                f"""
                <iframe width="560" height="315"
                src="{media_url}"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen>
                </iframe>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.write("No media available")
            
def render_workout_plan():
    """
    Render the workout plan page.
    """
    st.title("Workout Plan")

    # Check if the user completed the questionnaire
    if "responses" not in st.session_state:
        st.error("No responses found. Please complete the questionnaire first.")
        st.info("Navigate to Questionnaire from the Side Bar")
        st.stop()

    # Create workout plan
    if st.session_state["trigger_generate_plan"]:
        run_generate_workout_plan()

    # Display the workout plan
    plan = st.session_state.get("workout_plan", {})
    if plan:
        st.subheader(f"{plan['workout_title']}")
        st.markdown(f"Total Workout Duration: {
                    plan['total_workout_duration']} minutes")
        st.markdown(f"Number of Exercises: {plan['num_exercises']}")
        st.divider()
        # Display warmup section
        st.header("🔥 Warm-Up")

        st.markdown(
            f"**Duration:** {plan['warmup']['warmup_duration']} minutes")
        warmup_exercises = plan['warmup']['warmup_exercises']
        for exercise in warmup_exercises:
            st.subheader(f"{exercise["exercise_name"]}")
            st.markdown(f"**Setup:** {exercise['setup_notes']}")
            st.markdown(f"**Execution:** {exercise['execution_notes']}")

            

        st.divider()

        # Display workout sets
        st.subheader("Workout Sets")
        for set_data in plan.get("sets", []):
            outer_cols = st.columns([1, 3])  # Two columns: title and details

            # Column 1: Set title
            with outer_cols[0]:
                st.markdown(f"### Set {set_data['set_number']}")

            # Column 2: Set details with nested expanders
            with outer_cols[1]:
                with st.expander("Set Details", expanded=False):
                    # Set Details
                    st.markdown(
                        f"**Target Muscle Group(s):** {', '.join(set_data['target_muscle_group'])}")
                    st.markdown(
                        f"**Set strategy:** {set_data['set_strategy']}")
                    st.markdown(
                        f"**Set Duration:** {set_data['set_duration']} minutes")
                    st.markdown(
                        f"**Repetitions per Set:** {set_data['set_repetitions']}")

                    for exercise in set_data.get("exercises", []):
                        st.subheader(f"💪 {exercise['exercise_name']}")
                        st.markdown(f"**Target Muscle Part(s):** {', '.join(
                            [f'{k}: {', '.join(v)}' for k, v in exercise['target_muscle_part'].items()])}")
                        st.markdown(f"**Setup:** {exercise['setup']}")
                        st.markdown("**Execution:**")
                        for step in exercise["execution"]:
                            st.markdown(f"- {step}")
                        
                        # Display media for the main exercise
                        render_media(exercise.get("media_url", None))

                        st.markdown(f"**Reps:** {exercise['reps']}")
                        st.markdown(
                            f"**Weight Recommendation:** {exercise['weight']}")
                        st.markdown(f"**Rest Time:** {exercise['rest_time']}")
                        st.markdown(
                            f"**Alternative Equipment:** {exercise.get('alternative_equipments', 'None')}")
                        alternative = exercise.get(
                            'alternative_exercise', 'None')
                        
                        if alternative != "None":
                            with st.expander(f"🔄 Alternative Exercise: {alternative}"):
                                st.markdown(
                                    f"**Setup:** {exercise.get('alternative_exercise_setup', 'N/A')}")
                                st.markdown("**Execution:**")

                                for alt_step in exercise.get('alternative_exercise_execution', []):
                                    st.markdown(f"- {alt_step}")

                                # Add Media for Alternative Exercise
                                render_media(exercise.get(
                                "alternative_exercise_media_url", None))
    else:
        st.error("Please try to generate workout plan again")


if __name__ == "__main__":

    # secrets_path = os.path.join(os.path.dirname(__file__), "secrets.toml")
    # if os.path.exists(secrets_path):
    #     secrets = toml.load(secrets_path)
    # else:
    #     secrets = {}


    initialize_sessions_states()
    render_workout_plan()
