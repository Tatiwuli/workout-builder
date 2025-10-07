
import google.generativeai as genai
from dotenv import load_dotenv

import json
import time
import re


# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# assert OPENAI_API_KEY, "OPENAI_API_KEY is not set in the environment!"


class GeminiLLM:
    def __init__(self, model_name="models/gemini-2.5-flash", temperature=0.0, api_key=None):
        if not api_key:
            raise ValueError("Google API key is required.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={"temperature": temperature},
            safety_settings=[
                {"category": "HARM_CATEGORY_DANGEROUS", "threshold": 4}],
        )

    def call_api(self, system_prompt, user_prompt, assistant_prompt=None):
        full_prompt = ""
        if system_prompt:
            full_prompt += f"<system>\n{system_prompt.strip()}\n</system>\n\n"
        if assistant_prompt:
            full_prompt += f"<assistant>\n{assistant_prompt.strip()}\n</assistant>\n\n"
        full_prompt += f"<user>\n{user_prompt.strip()}\n</user>"

        try:
            response = self.model.generate_content(
                full_prompt
            )
        except Exception as e:
            raise RuntimeError(f"Gemini API call failed: {e}")

        response_text = response.text.strip()

        match = re.search(
            r"```(?:json)?\s*(\{.*\})\s*```", response_text, re.DOTALL)
        formatted_response_text = match.group(1) if match else response_text

        try:
            json_formatted_response_text = json.loads(formatted_response_text)
            return json_formatted_response_text
        except json.JSONDecodeError:
            raise RuntimeError(
                "Response was not valid JSON. Add clearer formatting instruction to your prompt.")
