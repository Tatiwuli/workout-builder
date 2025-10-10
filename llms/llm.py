
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
    def __init__(self, model_name: str | None = None, temperature: float = 0.0, api_key: str | None = None):
        if OpenAI is None:
            raise RuntimeError(
                "openai package not installed. Please add 'openai' to requirements.txt")
        load_dotenv()
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required.")
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-5-mini")
        self.temperature = temperature
        # Heuristic: use Responses API for any gpt-5* models
        self._use_responses_api = str(
            self.model_name).lower().startswith("gpt-5")

    def call_api(self, system_prompt: str, user_prompt: str, assistant_prompt: str | None = None):
        # Prepare a combined prompt for Responses API fallback
        full_prompt = ""
        if system_prompt:
            full_prompt += f"<system>\n{system_prompt.strip()}\n</system>\n\n"
        if assistant_prompt:
            full_prompt += f"<assistant>\n{assistant_prompt.strip()}\n</assistant>\n\n"
        full_prompt += f"<user>\n{user_prompt.strip()}\n</user>"

        def _call_with_model(model_id: str) -> str:
            use_responses = str(model_id).lower().startswith(
                "gpt-5") and hasattr(self.client, "responses")
            if use_responses:
                resp = self.client.responses.create(
                    model=model_id,
                    input=full_prompt,
                    temperature=self.temperature,
                )
                if hasattr(resp, "output_text") and resp.output_text:
                    return str(resp.output_text)
                try:
                    output = getattr(resp, "output", None)
                    if output and isinstance(output, list) and output:
                        content = getattr(output[0], "content", None)
                        if content and isinstance(content, list) and content:
                            text = getattr(content[0], "text", None)
                            if text:
                                return str(text)
                except Exception:
                    pass
                return str(resp)
            else:
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
                    model=model_id,
                    temperature=self.temperature,
                    messages=messages,
                )
                return (resp.choices[0].message.content or "").strip()

        try:
            response_text = _call_with_model(self.model_name)
        except Exception as e:
            msg = str(e).lower()
           
            else:
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
