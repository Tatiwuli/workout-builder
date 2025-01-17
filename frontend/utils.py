import streamlit as st


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
        "I'm just starting out and have less than 3 months of experience." : "Early Beginner",
        "I’ve been consistently training for 3 months to 1 year." : "Beginner",
        "I’ve been training regularly for 1 to 3 years." : "Early Intermediate",
        "I’m a seasoned lifter with over 3 years of training experience." : "Late Intermediate"
    }
    user_responses["experience_level"] = experience_mapping.get(
        user_responses.get("experience_level"), "Unknown"
    )

    muscle_goals = {
        muscle: goal
        for muscle, goal in user_responses.items()
        if muscle.endswith("_goal") and goal
    }

    muscle_workout_frequency = {
        muscle: frequency
        for muscle, frequency in user_responses.items()
        # Only include valid frequencies
        if muscle.endswith("_frequency") and frequency
    }

    final_user_responses = {
        # List of selected muscles
        "muscle_groups": user_responses.get("muscle_groups"),
        "goals": muscle_goals,
        "muscle_workout_frequency": muscle_workout_frequency,
        "workout_duration": workout_duration,
        "time_range": user_responses.get("time_range"),
        "experience_level": user_responses.get("experience_level"),
    }

    return final_user_responses

def render_nav_link(page_name):
    """
    Render a navigation link styled as a button to navigate between pages dynamically.
    """
    # Dynamically construct the base URL
    full_base_url = "https://workout-builder.streamlit.app"



    # Render the button as a styled hyperlink
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
        <a href="{full_base_url}/{page_name}" target="_self" class="btn">
            Go to {page_name.replace('_', ' ').capitalize()}
        </a>
        """,
        unsafe_allow_html=True,
    )
