import streamlit as st
from openai import OpenAIError


st.set_page_config(page_title="Workout Builder",
                   page_icon="💪", layout="centered")

from frontend.utils import render_nav_link


def validate_api_key(api_key):
    """Validate the provided OpenAI API key."""
    import openai
    try:
        openai.api_key = api_key
        openai.Model.list()  # Lightweight validation
        return True
    except OpenAIError:
        return False


def home():
    # Initialize session state for the user
    if "user" not in st.session_state:
        st.session_state["user"] = {"api_key": None}

    # Display UI
    st.title("🏋️‍♂️ Workout Builder")
    st.subheader(
        "Create personalized, science-backed workout plans tailored to your goals!")

    st.info("""
        **This is still an MVP. Please provide your OpenAI API key to test the app.**
        If you don't have one, create one [here](https://platform.openai.com/account/api-keys).
    """)

    with st.form(key="api_key_form"):
        st.write("Enter your OpenAI API key:")
        user_api_key = st.text_input(
            "API Key", type="password", value=st.session_state["user"]["api_key"] or "")
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            if user_api_key:
                # Validate API key
               
                st.session_state["user"]["api_key"] = user_api_key
                st.success("API Key successfully validated and saved!")
                st.write(st.session_state["user"]["api_key"])
                st.info("Navigate to the Questionnaire page on the sidebar.")

                
                
              
            else:
                st.error("API Key is required.")

if __name__ == "__main__":
    home()
