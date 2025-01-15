
import streamlit as st
from streamlit_modal import Modal


# Function to handle logout


def logout_user(cookies):
    """
    Handles user logout by clearing the API key and timestamp from cookies.
    """
    if "api_key" in cookies:
        del cookies["api_key"]
    if "api_key_timestamp" in cookies:
        del cookies["api_key_timestamp"]

    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.success(
        "You have been logged out. Please re-enter your API key to continue.")
    st.stop()

# Function to render logout mechanism


def render_logout(cookies):
    """
    Renders the logout button in the sidebar and handles the logout flow.
    """

    
    modal = Modal(title="Confirm Logout", key="logout_modal", max_width=600)

    with st.sidebar:
        st.subheader("Account")
        if st.button("Logout"):
            modal.open()

    # If modal is open, display logout confirmation
    if modal.is_open():
        with modal.container():
            st.warning(
                "⚠️Are you sure you want to log out? This will remove your API key and other saved data.")

            col1, col2 = st.columns([5, 20])
            with col1:

                if st.button("Yes, Logout"):
                    logout_user(cookies)

            with col2:
                if st.button("Cancel"):
                    modal.close()




def render_nav_link(page_path):
    """
    Render a navigation link styled as a button to return to the questionnaire.
    """
    app_path = 'http://localhost:8501'
    page_file_path = page_path
    page = page_file_path.split('/')[0]

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
        <a href="{app_path}/{page}" target="_self" class="btn">
            Go to {page_path}
        </a>
        """,
        unsafe_allow_html=True,
    )
