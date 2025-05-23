
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")))

from frontend.questionnaire_utils import goal_question, frequency_question, duration_question, experience_question
from frontend.utils import process_user_responses
from frontend.run_generate_workout_plan import trigger_generate_workout_plan
import streamlit as st
import time

#Config
st.set_page_config(page_title="Questionnaire",
                   page_icon="📝", layout="centered")




PULL_OPTIONS = ["Biceps", "Back"]
PUSH_OPTIONS = ["Chest", "Shoulders", "Triceps"]
LEG_OPTIONS = ["Glutes", "Hamstrings", "Quadriceps", "Calves"]
QUESTIONS = ["Goal", "Frequency", "Duration", "Experience"]

# ---------- Handlers ----------

# Question Navigation buttons

def go_back():
    if st.session_state["question_index"] > 0:
        st.session_state["question_index"] -= 1


def go_next():
    current_question = QUESTIONS[st.session_state["question_index"]]
    # Save current response

    st.session_state["responses"][current_question] = st.session_state["current_response"]
    if st.session_state["question_index"] < len(QUESTIONS) - 1:
        st.session_state["question_index"] += 1

#Initialize

def initialize_session_state():
    """
    Initialize session state variables.
    """
    if "responses" not in st.session_state:
        st.session_state["responses"] = {}
    if "processed_responses" not in st.session_state:
        st.session_state["processed_responses"] = {}

    if "is_last_question" not in st.session_state:
        st.session_state["is_last_question"] = False

    if "question_index" not in st.session_state:
        st.session_state["question_index"] = 0

    if "all_selected_muscles" not in st.session_state:
        st.session_state["all_selected_muscles"] = None
    if "current_response" not in st.session_state:
        st.session_state["current_response"] = None

    if "trigger_generate_plan" not in st.session_state:
        st.session_state["trigger_generate_plan"] = False

    if "workflow_stage" not in st.session_state:
        st.session_state["workflow_stage"] = "muscle_selection"

    if "plan_generated" not in st.session_state:
        st.session_state["plan_generated"] = False

#Confirmation Button
def confirm_muscle_selection():
    """
    Confirm selected muscles and transition to the questionnaire.
    """
    selected_muscles = [
        muscle
        for muscle in PULL_OPTIONS + PUSH_OPTIONS + LEG_OPTIONS
        if st.session_state.get(muscle)
    ]

    if len(selected_muscles) == 0:
        st.error("Please select at least one muscle group.")
    elif len(selected_muscles) > 4:
        st.error("Please select up to 4 muscle groups.")
    else:
        st.session_state["workflow_stage"] = "questionnaire"

        st.session_state["question_index"] = 0
        st.session_state["all_selected_muscles"] = selected_muscles
        st.session_state["responses"] = {}

# ---------- Rendering Functions ----------


def render_muscle_selection():
    """
    Render the muscle selection interface.
    """
    def toggle_select_all(section_key, muscles):
        """
        Toggles the state of all checkboxes in a section based on the "Select All" checkbox.
        """
        select_all_key = f"{section_key}_select_all"
        if st.session_state.get(select_all_key, False):  # If "Select All" is checked
            for muscle in muscles:
                st.session_state[muscle] = True
        else:  # If "Select All" is unchecked
            for muscle in muscles:
                st.session_state[muscle] = False


    col1, col2 = st.columns(2)
    all_selected = []
    with col1:
        with st.expander("Pull Section", expanded=True):
            st.subheader("Pull Section")
            pull_select_all = st.checkbox("Select All", key="pull_select_all",
                                          on_change=toggle_select_all, args=("pull", PULL_OPTIONS))
            for muscle in PULL_OPTIONS:
                st.checkbox(muscle, key=muscle)
                

        with st.expander("Push Section", expanded=True):
            st.subheader("Push Section")
            push_select_all = st.checkbox("Select All", key="push_select_all",
                                          on_change=toggle_select_all, args=("push", PUSH_OPTIONS))
            for muscle in PUSH_OPTIONS:
                st.checkbox(muscle, key=muscle)
                

    with col2:
        with st.expander("Leg Section", expanded=True):
            st.subheader("Leg Section")
            leg_select_all = st.checkbox("Select All", key="leg_select_all",
                                         on_change=toggle_select_all, args=("leg", LEG_OPTIONS))
            for muscle in LEG_OPTIONS:
                st.checkbox(muscle, key=muscle)
                
    all_selected = [muscle for muscle in LEG_OPTIONS+PULL_OPTIONS + PUSH_OPTIONS if st.session_state.get(muscle)]
    if len(all_selected) > 4:
        st.error("Please select up to 4 muscles")
        
    # Display selected muscle groups
    st.subheader("Selected Muscle Groups")
    st.write(", ".join(all_selected)
             if all_selected else "No muscles selected.")

    
    
    
    st.button("Confirm Selections", on_click=confirm_muscle_selection)
    

def render_questionnaire():
    """
    Display the questionnaire 
    """

    st.subheader("Selected Muscle Groups")

    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(
            ", ".join(st.session_state["all_selected_muscles"]) or "No muscles selected.")

    with col2:
        # If button Edit is clicked
        if st.button("Edit"):
            # Display Muscle Selection section
            st.session_state["workflow_stage"] = "muscle_selection"
            st.rerun()  # Restart the Muscle Selection section

    current_question_index = st.session_state["question_index"]

    current_question = QUESTIONS[current_question_index]

    # Questions
    with st.form(f"{current_question}_form"):
        if current_question == "Goal":
            st.subheader("Set Your Goals")
            for muscle in st.session_state["all_selected_muscles"]:
                selected_options, selected_option = goal_question(muscle)
                st.session_state["responses"][f"{
                    muscle}_goal"] = selected_options or [selected_option]

        elif current_question == "Frequency":
            st.subheader("Set Workout Frequency")
            for muscle in st.session_state["all_selected_muscles"]:
                response = frequency_question(muscle)
                st.session_state["responses"][f"{muscle}_frequency"] = response

        elif current_question == "Duration":
            st.subheader("Set Workout Duration")
            response = duration_question()
            st.session_state["responses"]["workout_duration"] = response

        elif current_question == "Experience":
            st.subheader("Set Experience Level")
            response = experience_question()
            st.session_state["responses"]["experience_level_description"] = response

        # If current question is not the last question
        if not current_question_index == len(QUESTIONS) - 1:
            st.session_state["is_last_question"] = False
            # Save responses for different questions
            if st.form_submit_button("Save"):
                if current_question == "Goal":
                    st.session_state["current_response"] = selected_options or [
                        selected_option]
                else:
                    st.session_state["current_response"] = response

        # If it's last question
        if current_question_index == len(QUESTIONS) - 1:
            st.session_state["is_last_question"] = True
            if st.form_submit_button("Submit"):

                # Display completion message
                complete_message = st.empty()
                complete_message.success("Questionnaire complete! 🎉")
                time.sleep(2)
                complete_message.empty()

                # Retrieve responses
                responses = st.session_state["responses"]
                # Save selected muscle groups
                responses["muscle_groups"] = st.session_state["all_selected_muscles"]

                # Switch to workout plan stage
                st.session_state["workflow_stage"] = "workout_plan"
                st.rerun()  # update the stage
                st.write(st.session_state["workflow_stage"])

    if st.session_state["is_last_question"] == False:
        # navigation buttons
        col1, col2 = st.columns([5, 45])  # next to each other
        with col1:
            st.button("⬅️", on_click=go_back)
        with col2:
            st.button("➡️", on_click=lambda: go_next())


def render_formatted_responses(processed_responses):

    # Grouping data for structured display with emojis
    grouped_data = {
        "General Info": {
            "💪 Muscle groups": ", ".join(processed_responses.get("muscle_groups", [])),
            "⏳ Workout duration": processed_responses.get("workout_duration"),
            "📏 Time range": processed_responses.get("time_range"),
            "🏋️‍♀️ Experience level": processed_responses.get("experience_level"),
        },
        "🎯 Goals": processed_responses.get("goals", {}),
        "📅 Frequency": processed_responses.get("muscle_workout_frequency", {})

    }

    # Display grouped data
    for group_name, group_values in grouped_data.items():
        st.markdown(f"### {group_name}")
        if isinstance(group_values, dict):
            for muscle, value in group_values.items():
                st.markdown(f"- **{muscle}:** {value}")
        elif isinstance(group_values, str):
            st.markdown(f"- **{group_name}:** {group_values}")
        elif isinstance(group_values, list):
            st.markdown(f"- **{group_name}:** {', '.join(group_values)}")
        else:
            for key, value in group_values.items():
                st.markdown(f"- **{key}:** {value}")


# ---------- Main Logic ----------
if __name__ == "__main__":

    initialize_session_state()

    if st.session_state["workflow_stage"] == "muscle_selection":

        st.title("Select Your Workout Muscles")
        # if "user" not in st.session_state or not st.session_state["user"].get("api_key"):
        #     st.error(
        #         "API Key is missing. Please go back to the Home page to provide it.") FOR OPENAI
        # else:
        render_muscle_selection()

    elif st.session_state["workflow_stage"] == "questionnaire":
        st.title("Let's get to know more about you")
        render_questionnaire()

    elif st.session_state["workflow_stage"] == "workout_plan":

        responses = st.session_state["responses"]

        # Show user responses
        st.header("Your Responses")
        processed_responses = process_user_responses(responses)
        st.session_state["processed_responses"] = processed_responses

        render_formatted_responses(processed_responses)

        if not st.session_state.get("plan_generated", False):
            # If the plan is not generated yet
            if st.button("Generate Workout Plan", on_click=trigger_generate_workout_plan,
                         disabled=st.session_state["trigger_generate_plan"]):
                st.info(
                    "Your workout plan is being built. Navigate to the Workout Plan page.")
                st.session_state["plan_generated"] = True
        else:
            # If the plan has already been generated, show "Make Another Plan" button
            if st.button("Make Another Plan"):
                # Reset session state va
                # riables for a new plan
                st.session_state["workflow_stage"] = "muscle_selection"
                st.session_state["plan_generated"] = False

                st.rerun()
