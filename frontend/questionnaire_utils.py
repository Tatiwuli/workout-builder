import streamlit as st 

def frequency_question(muscle):
    existing_response = st.session_state["responses"].get(
        f"{muscle}_frequency", 1)
    response = st.number_input(
        f"How many times do you plan to work on {muscle} per week?",
        min_value=1,
        max_value=7,
        value=existing_response,
        step=1,
        key=f"{muscle}_frequency"
    )
    return response


def experience_question():

    experience_options = [
        "I'm just starting out and have less than 3 months of experience.",
        "I’ve been consistently training for 3 months to 1 year.",
        "I’ve been training regularly for 1 to 3 years.",
        "I’m a seasoned lifter with over 3 years of training experience."
    ]
    existing_response = st.session_state["responses"].get(
        "experience_level_explanation", None)
    response = st.radio(
        "What's your experience level with weightlifting?",
        experience_options,
        index=experience_options.index(
            existing_response) if existing_response else 0,
        key="experience_level_explanation"
    )
    return response


def duration_question():
    existing_response = st.session_state["responses"].get(
        "workout_duration", 30)
    response = st.number_input(
        "How long do you have for this workout? (in minutes)",
        min_value=10,
        max_value=180,
        value=existing_response,
        step=5,
        key="workout_duration"
    )
    return response


def goal_question(muscle):
    goal_options = {
        "Biceps": ["Bigger biceps", "Peak in biceps", "Overall biceps definition"],
        "Triceps": ["Thicker triceps",  "Overall triceps definition"],
        "Chest": ["Upper chest focus for a fuller look", "Overall chest definition"],
        "Shoulders": ["3D look for shoulders", "Broader shoulders for a V-taper", "Overall shoulder definition"],
        "Back": ["Increase width", "Thicker back", "Overall back definition"],
        "Glutes": ["Lifted glutes", "Overall glutes development"],
        "Hamstrings": ["Toned hamstrings", "Bigger hamstrings"],
        "Quadriceps": ["Defined quads", "Bigger quads"],
        "Calves": ["Defined calves", "Bigger calves"],
    }
    # shoulders andback should have multiselection
    if muscle in ["Shoulders", "Back"]:
        # Retrieve existing responses and filter invalid options
        existing_response = st.session_state["responses"].get(
            f"{muscle}_goal", [])
        # ensure that the default value matches an option
        valid_defaults = [
            option for option in existing_response if option in goal_options[muscle]]

        # Render multiselect
        selected_options = st.multiselect(
            f"{muscle} (Multi-selection allowed):",
            goal_options[muscle],
            default=valid_defaults  # Ensure only valid defaults are passed
        )
        return selected_options, None

    # Single-selection for other muscles
    else:
        # Retrieve existing response
        existing_response = st.session_state["responses"].get(
            f"{muscle}_goal", [None])[0]
        if existing_response not in goal_options[muscle]:
            # Default to the first option if invalid
            existing_response = goal_options[muscle][0]

        # Render radio
        selected_option = st.radio(
            f"{muscle} (Single-selection only):",
            goal_options[muscle],
            index=goal_options[muscle].index(existing_response)
        )
        return [], selected_option
