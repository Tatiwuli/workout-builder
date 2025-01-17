
import streamlit as st


def render_nav_link(page_name):
    """
    Render a navigation link styled as a button to navigate between pages dynamically.

    Args:
        page_name (str): Name of the page (e.g., 'questionnaire', 'workout_plan').
    """
    # Dynamically construct the base URL
    base_url = st.get_option("browser.serverAddress") or "localhost"
    port = st.get_option("server.port")
    full_base_url = f"http://{base_url}:{
        port}" if port else f"http://{base_url}"

    # Create a query parameter for navigation
    st.query_params.page = page_name

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
        <a href="{full_base_url}?page={page_name}" target="_self" class="btn">
            Go to {page_name.replace('_', ' ').capitalize()}
        </a>
        """,
        unsafe_allow_html=True,
    )
