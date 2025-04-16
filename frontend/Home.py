
import streamlit as st
from openai import OpenAIError
import os 
import sys

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../")))

st.set_page_config(page_title="Home",
                   page_icon="💪", layout="centered")


#Main 
def home():
    st.title("🏋️‍♂️ Personalized Workout Builder")

    st.markdown(
        """
        ### Create **personalized**, **science-backed** workout plans tailored to your goals.
        
        This app uses advanced AI trained on insights from:
        - 🎓 *Jeff Nippard’s* research-driven programs
        - 🧠 *Dr. Mike Israetel* & Renaissance Periodization’s hypertrophy principles

        Whether you're just starting out or optimizing your next phase, we’ve got you covered.
        """
    )

    st.markdown("## Ready to build your plan?")
    if st.button("📝 Start Questionnaire"):
        st.switch_page("pages/questionnaire.py")

    #render_nav_link("pages\questionnaire.py")

        
if __name__ == "__main__":
    home()
