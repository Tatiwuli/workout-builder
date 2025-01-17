
import streamlit as st
from streamlit_modal import Modal
from streamlit_cookies_manager import EncryptedCookieManager
from dotenv import load_dotenv
import os





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
