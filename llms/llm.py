
import google.generativeai as genai
from dotenv import load_dotenv

import json
import time
import re
import os

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # Optional dependency


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


class OpenAILLM:
    def __init__(self, model_name: str = "gpt-5", temperature: float = 0.0, api_key: str | None = None):
        if OpenAI is None:
            raise RuntimeError(
                "openai package not installed. Please add 'openai' to requirements.txt")
        load_dotenv()
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required.")
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        self.temperature = temperature
        # Heuristic: newer models like gpt-5/gpt-5-mini often require the Responses API
        self._use_responses_api = str(model_name).lower().startswith("gpt-5")

    def call_api(self, system_prompt: str, user_prompt: str, assistant_prompt: str | None = None):
        # Prepare a combined prompt for Responses API fallback
        full_prompt = ""
        if system_prompt:
            full_prompt += f"<system>\n{system_prompt.strip()}\n</system>\n\n"
        if assistant_prompt:
            full_prompt += f"<assistant>\n{assistant_prompt.strip()}\n</assistant>\n\n"
        full_prompt += f"<user>\n{user_prompt.strip()}\n</user>"

        try:
            if self._use_responses_api and hasattr(self.client, "responses"):
                # Use Responses API for gpt-5/gpt-5-mini
                resp = self.client.responses.create(
                    model=self.model_name,
                    input=full_prompt,
                    temperature=self.temperature,
                )
                # Robust extraction: prefer output_text, else walk structure
                response_text = None
                if hasattr(resp, "output_text") and resp.output_text:
                    response_text = str(resp.output_text)
                else:
                    try:
                        # Attempt to navigate common structure
                        # resp.output[0].content[0].text
                        output = getattr(resp, "output", None)
                        if output and isinstance(output, list) and output:
                            content = getattr(output[0], "content", None)
                            if content and isinstance(content, list) and content:
                                text = getattr(content[0], "text", None)
                                if text:
                                    response_text = str(text)
                    except Exception:
                        pass
                if not response_text:
                    # Fallback to string
                    response_text = str(resp)
            else:
                # Default to Chat Completions API
                messages = []
                if system_prompt:
                    messages.append(
                        {"role": "system", "content": system_prompt.strip()})
                if assistant_prompt:
                    messages.append(
                        {"role": "assistant", "content": assistant_prompt.strip()})
                messages.append(
                    {"role": "user", "content": user_prompt.strip()})

                resp = self.client.chat.completions.create(
                    model=self.model_name,
                    temperature=self.temperature,
                    messages=messages,
                )
                response_text = (resp.choices[0].message.content or "").strip()
        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {e}")

        match = re.search(
            r"```(?:json)?\s*(\{.*\})\s*```", response_text, re.DOTALL)
        formatted_response_text = match.group(1) if match else response_text

        try:
            json_formatted_response_text = json.loads(formatted_response_text)
            return json_formatted_response_text
        except json.JSONDecodeError:
            raise RuntimeError(
                "Response was not valid JSON. Add clearer formatting instruction to your prompt.")
