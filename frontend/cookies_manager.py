import os
from dotenv import load_dotenv
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager


class CookieManager:
    def __init__(self, prefix="workout_builder_"):
        """
        Initialize the EncryptedCookieManager with a prefix and password.
        """
        load_dotenv()
        self.password = os.getenv("COOKIE_PASSWORD")
        if not self.password:
            st.error("COOKIE_PASSWORD is not set. Please check your .env file.")
            raise ValueError("COOKIE_PASSWORD is missing")

        self.manager = EncryptedCookieManager(
            prefix=prefix, password=self.password)

    def is_ready(self):
        """
        Check if the cookie manager is ready to use.
        """
        return self.manager.ready()

    def save_api_key(self, api_key):
        """
        Save the API key in cookies.
        """
        if not self.is_ready():
            raise RuntimeError("Cookies are not ready")
        self.manager["api_key"] = api_key
        self.manager.save()

    def get_api_key(self):
        """
        Retrieve the API key from cookies.
        """
        if not self.is_ready():
            raise RuntimeError("Cookies are not ready")
        return self.manager.get("api_key", None)
