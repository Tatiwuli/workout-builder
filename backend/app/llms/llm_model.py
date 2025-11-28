import random
import time
from typing import Dict, Any, Optional, Tuple

from .llm import GeminiLLM, OpenAILLM


class LLMService:
    def __init__(
        self,
        *,
     
        retries: int = 1,
        base_delay: float = 0.5,
    ) -> None:
        self.gemini = GeminiLLM() 
        self.openai = OpenAILLM()
        self.retries = max(0, retries)
        self.base_delay = max(0.0, base_delay)

    def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Optional[Any] = None,
        prompt_cache_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Attempt Gemini with exponential backoff; fall back to OpenAI if Gemini
        exhausts its retries.
        """
        delay = self.base_delay
        last_exception: Optional[Exception] = None

        openai_format = response_model
        gemini_schema = None
        if response_model is not None:
            if hasattr(response_model, "model_json_schema"):
                gemini_schema = response_model.model_json_schema()
            else:
                gemini_schema = response_model

        for attempt in range(self.retries + 1):
            try:
                print("Calling Gemini")
                return self.gemini.call_llm(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_model=gemini_schema,
                )

            except Exception as exc:
                print("Gemini failed: ", exc)
                last_exception = exc
                if attempt == self.retries:
                    break

                print("Trying exponential backoff")
                sleep_for = delay * random.uniform(0.8, 1.2)
                if sleep_for > 0:
                    time.sleep(sleep_for)
                delay *= 2

        # Gemini exhausted; fall back to OpenAI.
        print("Gemini all attempts exhausted. Trying OpenAI")
        try:
            return self.openai.call_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=openai_format,
                prompt_cache_key=prompt_cache_key,
            )
           
        except Exception as exc:
            if last_exception is not None:
                exc.__cause__ = last_exception  # type: ignore[attr-defined]
            raise

    def call_stream_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Optional[Any] = None,
        prompt_cache_key: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Attempt Gemini streaming call with a single retry; fall back to OpenAI
        streaming call if Gemini fails.
        """
        delay = self.base_delay
        last_exception: Optional[Exception] = None

        gemini_schema = None
        openai_format = response_model
        if response_model is not None:
            if hasattr(response_model, "model_json_schema"):
                gemini_schema = response_model.model_json_schema()
            else:
                gemini_schema = response_model

        for attempt in range(self.retries + 1):
            try:
                print("Trying gemini ")
                response, metadata = self.gemini.call_stream_llm(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_model=gemini_schema,
                )
                   
                
                # Return valid response
                return response, metadata
            except Exception as exc:
                last_exception = exc
                if attempt == self.retries:
                    break

                sleep_for = delay * random.uniform(0.8, 1.2)
                if sleep_for > 0:
                    time.sleep(sleep_for)
                delay *= 2

        if self.openai is None:
            if last_exception:
                raise last_exception
            raise RuntimeError("Streaming LLMs are not configured")

        try:
            print("Gemini all attempts exhausted. Trying OpenAI", flush=True)
            openai_response, openai_metadata = self.openai.call_stream_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=openai_format,
                prompt_cache_key=prompt_cache_key,
            )
         
            return openai_response, openai_metadata
        except Exception as exc:
            if last_exception is not None:
                exc.__cause__ = last_exception 
            raise
