
from streamlit_cookies_manager import EncryptedCookieManager
from frontend.utils import render_nav_link, render_logout
import os
from dotenv import load_dotenv
import sys
import streamlit as st

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(page_title="Workout Builder",
                   page_icon="💪", layout="centered")


def home():
    # Initialize the cookie manager
    load_dotenv()
    COOKIE_PASSWORD =  st.secrets.get(
        "COOKIE_PASSWORD") or os.getenv("COOKIE_PASSWORD")
    cookies = EncryptedCookieManager(
        prefix="workout_builder_", password=COOKIE_PASSWORD)
    if not cookies.ready():
        st.stop()

    render_logout(cookies)

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
            "API Key", type="password", help="Your API key is securely encrypted and stored as a cookie in your browser. It is never sent to our servers and will automatically expire after 30 minutes.")

        submit_button = st.form_submit_button("Submit")

        if submit_button:
            if user_api_key:
                # Save the API key to session state

                user_api_key = user_api_key.strip()

                cookies["api_key"] = user_api_key
                cookies.save()

                if cookies.get("api_key"):
                    st.success(
                        "API Key successfully saved! You can now proceed.")
                    render_nav_link("Questionnaire")
                else:
                    st.error("API Key not saved. Please try again")

            else:
                st.error("API Key is required to proceed.")


# Run the home function
if __name__ == "__main__":
    home()
