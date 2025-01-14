import streamlit as st
import time

from frontend.run_generate_workout_plan import trigger_generate_workout_plan
from questionnaire_utils import goal_question, frequency_question, duration_question, experience_question

# Constants
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

def handler_initialize_session_state():
    """
    Initialize session state variables.
    """
    if "responses" not in st.session_state:
        st.session_state["responses"] = {}
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



def handler_confirm_muscle_selection():
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
    st.title("Select Your Workout Muscles")
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

    st.subheader("Selected Muscle Groups")
    all_selected = [
        muscle for muscle in PULL_OPTIONS + PUSH_OPTIONS + LEG_OPTIONS if st.session_state.get(muscle)
    ]
    st.write(", ".join(all_selected)
             if all_selected else "No muscles selected.")

    st.button("Confirm Selections", on_click= handler_confirm_muscle_selection)


def render_questionnaire():
    
    st.title("Questionnaire")
    st.subheader("Selected Muscle Groups")
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(
            ", ".join(st.session_state["all_selected_muscles"]) or "No muscles selected.")
    with col2:
        if st.button("Edit"): #If button Edit is clicked
            st.session_state["workflow_stage"] = "muscle_selection" #display muscle selection
            st.rerun() #restart the muscle selection

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
                response = frequency_question(muscle)
                st.session_state["responses"][f"{ muscle}_frequency"] = response

        elif current_question == "Duration":
            st.subheader("Set Workout Duration")
            response = duration_question()
            st.session_state["responses"]["workout_duration"] = response

        elif current_question == "Experience":
            st.subheader("Set Experience Level")
            response = experience_question()
            st.session_state["responses"]["experience_level_explanation"] = response

        #If current question is not the last question
        if not current_question_index == len(QUESTIONS) - 1:
            #Save responses for different questions
            if st.form_submit_button("Save"):
                if current_question == "Goal":
                    st.session_state["current_response"] = selected_options or [
                        selected_option]
                else:
                    st.session_state["current_response"] = response

        #if it's last question
        if current_question_index == len(QUESTIONS) - 1:
            if st.form_submit_button("Submit"):
                
                # Display completion message
                complete_message = st.empty()
                complete_message.success("Questionnaire complete! 🎉")
                time.sleep(2)
                complete_message.empty()

                # Retrieve responses
                responses = st.session_state["responses"]
                #Save selected muscle groups 
                responses["muscle_groups"] = st.session_state["all_selected_muscles"]
                
                
                #switch to workout plan stage
                st.session_state["workflow_stage"] = "workout_plan"
                st.rerun() #update the stage 
                st.write(st.session_state["workflow_stage"])


# ---------- Main Logic ----------
handler_initialize_session_state()


if st.session_state["workflow_stage"] == "muscle_selection":
    render_muscle_selection()

elif st.session_state["workflow_stage"] == "questionnaire":

    render_questionnaire()
    #navigation buttons
    col1, col2 = st.columns([5, 45])  # next to each other
    with col1:
        st.button("⬅️", on_click=go_back)
    with col2:
        st.button("➡️", on_click=lambda: go_next())

elif st.session_state["workflow_stage"] == "workout_plan":
    responses = st.session_state["responses"]
    # Show user responses
    st.subheader("Your Responses")
    for key, value in responses.items():
        if isinstance(value, list):
            value = ", ".join([str(v)
                                for v in value if v]) or "No response"
        col1, col2 = st.columns([1, 3])
        col1.write(f"**{key.replace('_', ' ').capitalize()}:**")
        col2.write(value)

    # if user clicks "Generate Workout Plan"
    if st.button("Generate Workout Plan", on_click=trigger_generate_workout_plan,
                 # trigger the function that generate plan
                 disabled=st.session_state["trigger_generate_plan"],):
        st.info("Your workout plan is being built. Navigate to Workout Plan page")
