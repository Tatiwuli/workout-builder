from google import genai
from google.genai import types
from dotenv import load_dotenv
import json
import time
import re
import os
from typing import Dict, Any, Optional

from openai import OpenAI


from ..utils.agent_utils import save_output_to_json




class GeminiLLM:
    def __init__(self, model_name="gemini-2.5-flash"):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is required in environment")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: Optional[Dict[str, Any]] = None,
        
    ) -> Dict[str, Any]:
        """
        Calls the Gemini LLM API with system and user prompts.

        Args:
            system_prompt (str): System instruction for the model
            user_prompt (str): User content/query
            json_schema (Optional[Dict[str, Any]]): JSON schema for structured output
            stream_responses (bool): Unused placeholder for parity with other interfaces.

        Returns:
            Dict[str, Any]: Parsed JSON response from the LLM

        Raises:
            RuntimeError: If API call fails or response cannot be parsed
        """

        config_params = {
            "system_instruction": system_prompt,
            "temperature": 0.3,
            "thinking_config": types.ThinkingConfig(thinking_budget=-1),  # dynamic
        }

        if json_schema:
            config_params["response_mime_type"] = "application/json"
            config_params["response_json_schema"] = json_schema

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(**config_params),
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
            # still try to extract from markdown code blocks as fallback
            match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", response_text)
            payload = match.group(1) if match else response_text

            return json.loads(payload)

        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse JSON from Gemini: {e}\nRaw: {response_text[:400]}...")

    def call_stream_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        config_params = {
            "system_instruction": system_prompt,
            "temperature": 0.3,
            "thinking_config": types.ThinkingConfig(thinking_budget=-1),  # dynamic
        }

        if json_schema:
            config_params["response_mime_type"] = "application/json"
            config_params["response_json_schema"] = json_schema

        metadata = {
            "model": self.model_name,
            "system_prompt": system_prompt[:300],
            "tokens": 0,
            "time_first_token": 0.0,
            "total_time": 0.0,
            "output_gen_time": 0.0,
            "tokens_per_second": 0.0,
            "avg_token_per_sec": 0.0,
            "status": "started",
            "error": None,
        }

        try:
            start = time.time()
            response = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(**config_params),
            )
            full_response = ""
            tokens = 0
            first_token_time = None
            last_time = None

            for chunk in response:
                chunk_type = getattr(chunk, "type", chunk.__class__.__name__)
                chunk_text = getattr(chunk, "text", None)
                chunk_usage = getattr(chunk, "usage_metadata", None)
                finish_reason = getattr(chunk, "finish_reason", None)
                print(
                    "[Gemini stream]"
                    f" type={chunk_type}"
                    f" text={repr(chunk_text)}"
                    f" usage={chunk_usage}"
                    f" finish_reason={finish_reason}",
                    flush=True,
                )
                if chunk_text:
                    full_response += chunk_text
                    if first_token_time is None:
                        first_token_time = time.time()
                    last_time = time.time()

                if chunk_usage and hasattr(chunk_usage, "candidates_token_count"):
                    tokens = chunk_usage.candidates_token_count

            if not full_response.strip():
                raise RuntimeError("Empty streaming response from Gemini")

            first_token_time = first_token_time or start
            last_time = last_time or first_token_time

            time_first_token = first_token_time - start
            total_time = last_time - start
            output_gen_time = last_time - first_token_time

            metadata.update(
                {
                    "tokens": tokens,
                    "time_first_token": time_first_token,
                    "total_time": total_time,
                    "output_gen_time": output_gen_time,
                    "tokens_per_second": tokens / output_gen_time if output_gen_time > 0 else 0,
                    "avg_token_per_sec": tokens / total_time if total_time > 0 else 0,
                    "status": "success",
                }
            )

            print("\n\n\n#########################")
            print("response: ", full_response)
            print("\n\n\n ##############################")
            print("\n\n\n#########################")
            print("metadata: ", metadata)
            print("\n\n\n ##############################")

            match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", full_response)
            payload = match.group(1) if match else full_response
            return json.loads(payload)
        except Exception as e:
            metadata["status"] = "error"
            metadata["error"] = str(e)
            raise
        finally:
            save_output_to_json(metadata, "metadata_tokens")






class OpenAILLM:
    def __init__(self, model_name="gpt-5-mini-2025-08-07"):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY is required in environment")

        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Calls the OpenAI LLM API with system and user prompts using Responses API.

        Args:
            system_prompt (str): System instruction for the model
            user_prompt (str): User content/query
            json_schema (Optional[Dict[str, Any]]): JSON schema for structured output

        Returns:
            Dict[str, Any]: Parsed JSON response from the LLM

        Raises:
            RuntimeError: If API call fails or response cannot be parsed
        """

        config_text = {}
        if json_schema:
            config_text["response_format"] = { 
                    "type": "json_schema",
                "json_schema": {
                    "name": "response",
                    "strict": True,
                    "schema": json_schema}
            }
        try:
            response = self.client.responses.create(
                model = self.model_name, 
            input = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
                **config_text,

            )
        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {e}")

        response_text = response.output_text
        print("\n\n\n#########################")
        print("response: ", response_text)
        print("\n\n\n ##############################")

        if not response_text:
            raise RuntimeError("Empty response text from OpenAI")

        try:
            match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", response_text)
            payload = match.group(1) if match else response_text

            return json.loads(payload)

        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"Failed to parse JSON from OpenAI: {e}\nRaw: {response_text[:400]}..."
            )

    def call_stream_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        
        

            
        config_text = {}
        if json_schema:
            config_text["response_format"] = { 
                    "type": "json_schema",
                "json_schema": {
                    "name": "response",
                    "strict": True,
                    "schema": json_schema}
            }


          
        first_token_time = None
        last_time = None
        metadata = {
            "model": self.model_name,
            "system_prompt": system_prompt[:300],
            "tokens": 0,
            "time_first_token": 0.0,
            "total_time": 0.0,
            "output_gen_time": 0.0,
            "tokens_per_second": 0.0,
            "avg_token_per_sec": 0.0,
            "status": "started",
            "error": None,
        }

        full_response = ""
        tokens = 0
        final_response = None

        try:
            start = time.time()
            with self.client.responses.stream(
                model=self.model_name,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                **config_text,
            ) as stream:
                for event in stream:
                    if event.type == "response.output_text.delta":
                        delta = getattr(event, "delta", None)
                        if delta:
                            full_response += delta
                            now = time.time()
                            if first_token_time is None:
                                first_token_time = now
                            last_time = now
                    elif event.type == "response.completed":
                        usage = getattr(event.response, "usage", None)
                        if usage:
                            tokens = usage.output_tokens
                    elif event.type == "response.error":
                        raise RuntimeError(f"OpenAI streaming error: {event.error}")
                final_response = stream.get_final_response()
        except Exception as e:
            metadata["status"] = "error"
            metadata["error"] = str(e)
            raise RuntimeError(f"OpenAI API call failed: {e}")
        finally:
            if not full_response and final_response:
                try:
                    full_response = final_response.output[0].content[0].text
                except (AttributeError, IndexError, TypeError):
                    full_response = ""

            if full_response:
                first_token_time = first_token_time or start
                last_time = last_time or first_token_time

                time_first_token = first_token_time - start
                total_time = last_time - start
                output_gen_time = last_time - first_token_time

                metadata.update(
                    {
                        "tokens": tokens,
                        "time_first_token": time_first_token,
                        "total_time": total_time,
                        "output_gen_time": output_gen_time,
                        "tokens_per_second": tokens / output_gen_time if output_gen_time > 0 else 0,
                        "avg_token_per_sec": tokens / total_time if total_time > 0 else 0,
                        "status": "success",
                    }
                )

            save_output_to_json(metadata, "metadata_tokens")

        if not full_response.strip():
            raise RuntimeError("Empty streaming response from OpenAI")

        print("\n\n\n#########################")
        print("response: ", full_response)
        print("\n\n\n ##############################")
        print("\n\n\n#########################")
        print("metadata: ", metadata)
        print("\n\n\n ##############################")

        match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", full_response)
        payload = match.group(1) if match else full_response
        return json.loads(payload)