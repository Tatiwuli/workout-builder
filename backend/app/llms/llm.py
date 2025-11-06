from google import genai
from google.genai import types
from dotenv import load_dotenv

import json

import re
import os



class GeminiLLM:
    def __init__(self, model_name="models/gemini-2.5-flash"):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required in environment")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name


    def call_llm(self, system_prompt: str, user_prompt: str):
        """
        Calls the Gemini LLM API with system and user prompts.
        
        Args:
            system_prompt (str): System instruction for the model
            user_prompt (str): User content/query
            
        Returns:
            dict: Parsed JSON response from the LLM
            
        Raises:
            RuntimeError: If API call fails or response cannot be parsed
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.3,
                    thinking_config=types.ThinkingConfig(thinking_budget=-1)  # dynamic
                ),
                
            )
        except Exception as e:
            raise RuntimeError(f"Gemini API call failed: {e}")

        response_text = response.candidates[0].content.parts[0].text
        print("\n\n\n#########################")
        print("response: ", response_text)
        print("\n\n\n ##############################")
        if not response_text:
            raise RuntimeError("Empty response text from Gemini")
        
        try:
            # Try to extract JSON from markdown code blocks first
            match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", response_text)
            payload = match.group(1) if match else response_text
            return json.loads(payload)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse JSON from Gemini: {e}\nRaw: {response_text[:400]}...")