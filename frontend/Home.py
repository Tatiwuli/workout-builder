import sys
import streamlit as st
from dotenv import load_dotenv
import os
from streamlit_cookies_manager import EncryptedCookieManager

st.set_page_config(page_title="Workout Builder",
                   page_icon="💪", layout="centered")

from frontend.utils import render_nav_link

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


def home():
    # Set up page configuration
    

    # Display the heading and subtitle
    st.title("🏋️‍♂️ Workout Builder")
    st.subheader(
        "Create personalized, science-backed workout plans tailored to your goals!")

    st.info("""
        **Because this is still an MVP, we kindly ask you to provide your own OpenAI API key to test out the app.**

        If you don't have one, you can create one here (https://platform.openai.com/account/api-keys).

        """)

    # Input form for the API key
    with st.form(key="api_key_form"):
        st.write("To get started, please provide your OpenAI API key:")
        user_api_key = st.text_input(
            "API Key", type="password", help= "Your API key is securely encrypted and stored as a cookie in your browser. It is never sent to our servers and will automatically expire after 30 minutes.")
        
        submit_button = st.form_submit_button("Submit")
        
        
        # Initialize the cookie manager
        load_dotenv()
        COOKIE_PASSWORD = os.getenv("COOKIE_PASSWORD")
        cookies = EncryptedCookieManager(prefix="workout_builder_", password=COOKIE_PASSWORD, max_age=1800)
        if not cookies.ready():
            st.stop()

        if submit_button:
            if user_api_key:
                # Save the API key to session state
                
                st.success("API Key successfully saved! You can now proceed.")
                render_nav_link("Questionnaire")
                
                user_api_key = user_api_key.strip()

                cookies["api_key"] = user_api_key
                print(user_api_key)
                cookies.save()
                
            else:
                st.error("API Key is required to proceed.")


# Run the home function
if __name__ == "__main__":
    home()
