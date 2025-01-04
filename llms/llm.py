
from token_count import TokenCount
from openai import OpenAI
from dotenv import load_dotenv

import json
import os
import time



load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY, "OPENAI_API_KEY is not set in the environment!"


class OpenAILLM:
    def __init__(self, model_name, temperature=0.0):
        self.model_name = model_name
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.max_retries = 2
        self.timeout = 90
        self.token_counter = TokenCount(model_name=model_name)
        self.temperature = temperature

    def count_total_tokens_cost(self, prompt_tokens, completion_tokens):

        model_pricing = {
            'gpt-4o': {'input': 2.50, 'output': 10.00},
            'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
            'gpt-3.5-turbo': {'input': 0.002, 'output': 0.002},
        }

        # Retrieve the pricing for the selected model
        if self.model_name in model_pricing:
            input_cost_per_million = model_pricing[self.model_name]['input']
            output_cost_per_million = model_pricing[self.model_name]['output']
        else:
            print(f"Pricing information for model '{
                  self.model_name}' is not available.")

        # Calculate the cost for the current API call
        input_cost = (prompt_tokens / 1_000_000) * input_cost_per_million
        output_cost = (completion_tokens / 1_000_000) * output_cost_per_million
        total_cost = input_cost + output_cost

        # Print token usage and cost information
        print(f"Model: {self.model_name}")
        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Completion tokens: {completion_tokens}")
        print(f"Total tokens: {prompt_tokens + completion_tokens}")
        print(f"Input cost: ${input_cost:.6f}")
        print(f"Output cost: ${output_cost:.6f}")
        print(f"Total cost: ${total_cost:.6f}")

        return total_cost

    def call_api(self, system_prompt, user_prompt):
        """
        Makes an API call to OpenAI with robust error handling.
        """
        retries = 0
        while retries < self.max_retries:
            try:
                print(f"Calling OpenAI API. Number of retries: {retries}")

                response = self.client.chat.completions.create(
                    model=self.model_name,
                    response_format={"type": "json_object"},
                    temperature=self.temperature,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    timeout=self.timeout
                )

                # Validate response
                if not response or not response.choices:
                    raise ValueError(
                        "Empty or invalid response received from the API.")

                response_string = response.choices[0].message.content

                try:
                    return json.loads(response_string)
                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON: {e}")
                    return None

            except Exception as e:
                retries += 1
                print(f"Error during API call (attempt {
                    retries}/{self.max_retries}): {e}")
                time.sleep(2)  # Delay between retries

        raise RuntimeError(
            "Failed to complete API call after two retries.")
