
import google.generativeai as genai
from token_count import TokenCount
from openai import OpenAI
from dotenv import load_dotenv

import json
import time


# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# assert OPENAI_API_KEY, "OPENAI_API_KEY is not set in the environment!"


class OpenAILLM:
    def __init__(self, model_name="models/gemini-1.5-flash", temperature=0.0, pydantic_format=None, api_key=None):
        self.model_name = model_name
        self.client = OpenAI(api_key=api_key)
        self.max_retries = 2
        self.timeout = 90
        self.token_counter = TokenCount(model_name=model_name)
        self.temperature = temperature
        self.pydantic_format = pydantic_format

    def count_total_tokens_cost(self, prompt_tokens, completion_tokens):
        model_pricing = {
            'models/gemini-1.5-flash': {'input': 2.50, 'output': 10.00},
            'models/gemini-1.5-flash-mini': {'input': 0.15, 'output': 0.60},
            'models/gemini-1.5-flash': {'input': 0.002, 'output': 0.002},
        }

        if self.model_name in model_pricing:
            input_cost_per_million = model_pricing[self.model_name]['input']
            output_cost_per_million = model_pricing[self.model_name]['output']
        else:
            raise ValueError(f"Pricing information for model '{
                             self.model_name}' is not available.")

        input_cost = (prompt_tokens / 1_000_000) * input_cost_per_million
        output_cost = (completion_tokens / 1_000_000) * output_cost_per_million
        total_cost = input_cost + output_cost

        print(f"Model: {self.model_name}")
        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Completion tokens: {completion_tokens}")
        print(f"Total tokens: {prompt_tokens + completion_tokens}")
        print(f"Input cost: ${input_cost:.6f}")
        print(f"Output cost: ${output_cost:.6f}")
        print(f"Total cost: ${total_cost:.6f}")

        return total_cost

    def call_api(self, system_prompt, user_prompt, assistant_prompt=None):
        """
        Makes an API call to OpenAI, including optional assistant prompts.
        """
        retries = 0
        while retries < self.max_retries:
            try:
                print(f"Calling OpenAI API. Retry attempt: {retries}")

                # Construct messages
                messages = [{"role": "system", "content": system_prompt}]
                if assistant_prompt:
                    messages.append(
                        {"role": "assistant", "content": assistant_prompt})
                messages.append({"role": "user", "content": user_prompt})

                # Make API call
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    response_format={"type": "json_object"},
                    temperature=self.temperature,
                    messages=messages,
                    timeout=self.timeout,
                )

                # Validate response
                if not response or not response.choices:
                    raise ValueError(
                        "Empty or invalid response received from the API.")

                response_string = response.choices[0].message.content

                # Parse JSON response
                try:
                    return json.loads(response_string)
                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON response: {e}")
                    return response_string  # Return raw string if JSON parsing fails

            except Exception as e:
                retries += 1
                print(f"Error during API call (attempt {
                      retries}/{self.max_retries}): {e}")
                time.sleep(2)

        raise RuntimeError(
            "Failed to complete API call after maximum retries.")


class GeminiLLM:
    def __init__(self, model_name="models/gemini-1.5-flash", temperature=0.0, api_key=None):
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
                full_prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except json.JSONDecodeError:
            raise RuntimeError(
                "Response was not valid JSON. Add clearer formatting instruction to your prompt.")
        except Exception as e:
            raise RuntimeError(f"Gemini API call failed: {e}")
