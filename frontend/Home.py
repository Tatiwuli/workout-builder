import streamlit as st
from openai import OpenAIError
import os 
import sys

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../")))

st.set_page_config(page_title="Workout Builder",
                   page_icon="💪", layout="centered")




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
               
                st.session_state["user"]["api_key"] = user_api_key
                st.success("🎉 API Key successfully validated and saved!")

                st.info("Navigate to the Questionnaire page on the sidebar.")

              
        
if __name__ == "__main__":
    home()
