import streamlit as st
import streamlit_nested_layout

from frontend.run_generate_workout_plan import  run_generate_workout_plan

st.set_page_config(page_title="Workout Plan", page_icon="💪")


if "workout_plan" not in st.session_state:
    st.session_state["workout_plan"] = None


def render_nav_link():
    """
    Render a navigation link styled as a button to return to the questionnaire.
    """
    app_path = 'http://localhost:8501'
    page_file_path = 'index'
    page = page_file_path.split('/')[0]

    st.markdown(
        f"""
        <style>
            .btn {{
                display: inline-block;
                font-weight: 400;
                text-align: center;
                white-space: nowrap;
                vertical-align: middle;
                user-select: none;
                border: 2px solid black;
                padding: 0.375rem 0.75rem;
                font-size: 1rem;
                line-height: 1.5;
                border-radius: 0.25rem;
                color: black;
                background-color: transparent;
                text-decoration: none;
                transition: all 0.3s ease-in-out;
            }}
            .btn:hover {{
                background-color: #FF4B4B;
                border-color: #FF4B4B;
                color: white;
            }}
        </style>
        <a href="{app_path}/{page}" target="_self" class="btn">
            Go to Questionnaire
        </a>
        """,
        unsafe_allow_html=True,
    )


def render_workout_plan():
    """
    Render the workout plan page.
    """
    st.title("Your Custom Workout Plan")

    # Ensure session state is properly initialized
    if "responses" not in st.session_state:
        st.error("No responses found. Please complete the questionnaire first.")
        render_nav_link()
        st.stop()

    #Create workout plan
    if st.session_state["trigger_generate_plan"]:
        run_generate_workout_plan()
    # Display the workout plan
    plan = st.session_state.get("workout_plan", {})
    if plan:
        st.subheader(f"{plan['workout_title']}")
        st.markdown(f"Total Workout Duration: {plan['total_workout_duration']} minutes")
        st.markdown(f"Number of Exercises: {plan['num_exercises']}")
        st.divider()
        # Display warmup section
        st.header("🔥 Warm-Up")

        st.markdown(f"**Duration:** {plan['warmup']['warmup_duration']} minutes")
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
                    st.markdown(f"**Set strategy:** {set_data['set_strategy']}")
                    st.markdown(f"**Set Duration:** {set_data['set_duration']} minutes")
                    st.markdown(f"**Repetitions per Set:** {set_data['set_repetitions']}")
                    
                    
                    for exercise in set_data.get("exercises", []):
                        st.subheader(f"💪 {exercise['exercise_name']}")
                        st.markdown(f"**Target Muscle Part(s):** {', '.join(
                            [f'{k}: {', '.join(v)}' for k, v in exercise['target_muscle_part'].items()])}")
                        st.markdown(f"**Setup:** {exercise['setup']}")
                        st.markdown("**Execution:**")
                        for step in exercise["execution"]:
                            st.markdown(f"- {step}")
                        st.markdown(f"**Reps:** {exercise['reps']}")
                        st.markdown(f"**Weight Recommendation:** {exercise['weight']}")
                        st.markdown(f"**Rest Time:** {exercise['rest_time']}")
                        st.markdown( f"**Alternative Equipment:** {exercise.get('alternative_equipments', 'None')}")
                        alternative= exercise.get('alternative_exercise', 'None')
                        if alternative != "None":
                            with st.expander(f"🔄 Alternative Exercise: {alternative}"):
                                st.markdown(f"**Setup:** {exercise.get('alternative_exercise_setup', 'N/A')}")
                                st.markdown("**Execution:**")

                                for alt_step in exercise.get('alternative_exercise_execution', []):
                                    st.markdown(f"- {alt_step}")
    else:
        st.error("Please try to generate workout plan again")

if __name__ == "__main__":
    render_workout_plan()
