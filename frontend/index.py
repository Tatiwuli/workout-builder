import streamlit as st

from questionnaire_utils import goal_question, frequency_question, duration_question, experience_question


# Constants
PULL_OPTIONS = ["Biceps", "Back"]
PUSH_OPTIONS = ["Chest", "Shoulders", "Triceps"]
LEG_OPTIONS = ["Glutes", "Hamstrings", "Quadriceps", "Calves"]
QUESTIONS = ["Goal", "Frequency", "Duration", "Experience"]

# Initialize session state


def initialize_session_state():
    if "responses" not in st.session_state:
        st.session_state["responses"] = {}
    if "question_index" not in st.session_state:
        st.session_state["question_index"] = 0
    if "start_user_preferences_questions" not in st.session_state:
        st.session_state["start_user_preferences_questions"] = False
    if "all_selected_muscles" not in st.session_state:
        st.session_state["all_selected_muscles"] = None

# Muscle selection logic


def display_muscle_selection():
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("Pull Section", expanded=True):
            st.subheader("Pull Section")
            for muscle in PULL_OPTIONS:
                st.checkbox(muscle, key=muscle)
        with st.expander("Push Section", expanded=True):
            st.subheader("Push Section")
            for muscle in PUSH_OPTIONS:
                st.checkbox(muscle, key=muscle)
    with col2:
        with st.expander("Leg Section", expanded=True):
            st.subheader("Leg Section")
            for muscle in LEG_OPTIONS:
                st.checkbox(muscle, key=muscle)

 
def handle_questionnaire_logic():
    st.subheader("Selected Muscle Groups")
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(
            ", ".join(st.session_state["all_selected_muscles"]) or "No muscles selected.")
    with col2:
        if st.button("Edit"):
            st.session_state["start_user_preferences_questions"] = False

    current_question_index = st.session_state["question_index"]
    current_question = QUESTIONS[current_question_index]

    with st.form(f"{current_question}_form"):
        if current_question == "Goal":
            st.subheader("Set Your Goals")
            for muscle in st.session_state["all_selected_muscles"]:
                selected_options, selected_option = goal_question(muscle)
                st.session_state["responses"][f"{muscle}_goal"] = selected_options or [selected_option]

        elif current_question == "Frequency":
            st.subheader("Set Workout Frequency")
            for muscle in st.session_state["all_selected_muscles"]:
                st.session_state["responses"][f"{muscle}_frequency"] = frequency_question(muscle)

        elif current_question == "Duration":
            st.subheader("Set Workout Duration")
            st.session_state["responses"]["workout_duration"] = duration_question()
        elif current_question == "Experience":
            st.subheader("Set Experience Level")
            st.session_state["responses"]["experience_level"] = experience_question(
            )

        col_back, col_next = st.columns(2)

        with col_back:
            if current_question_index > 0:
                back = st.form_submit_button("Back")
        with col_next:
            next = st.form_submit_button("Next")

    if "back" in locals() and back:
        st.session_state["question_index"] -= 1
    if next:
        if current_question_index < len(QUESTIONS) - 1:
            st.session_state["question_index"] += 1
        else:
            st.success("Questionnaire complete!")
            st.write("Your responses:", st.session_state["responses"])


# Main
initialize_session_state()

if not st.session_state["start_user_preferences_questions"]:
    display_muscle_selection()
    confirm_button = st.button("Confirm Selections")
    if confirm_button:
        selected_muscles = [muscle for muscle in PULL_OPTIONS +
                            PUSH_OPTIONS + LEG_OPTIONS if st.session_state.get(muscle)]
        if len(selected_muscles) == 0:
            st.error("Please select at least one muscle group.")
        elif len(selected_muscles) > 4:
            st.error("Please select up to 4 muscle groups.")
        else:
            st.session_state["start_user_preferences_questions"] = True
            st.session_state["question_index"] = 0
            st.session_state["all_selected_muscles"] = selected_muscles
            st.session_state["responses"] = {}

if st.session_state["start_user_preferences_questions"]:
    handle_questionnaire_logic()
