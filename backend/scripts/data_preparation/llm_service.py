import os
import re
import json
import time
import random
import logging
from typing import Dict, Any, Optional

from dotenv import load_dotenv

from ...app.llms.llm import GeminiLLM, OpenAILLM

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, retries: int = 2, base_delay: float = 0.5) -> None:
        load_dotenv()
        self.retries = retries
        self.base_delay = base_delay
        self.gemini = GeminiLLM()
        self.openai = OpenAILLM()

      

    def _extract_json(self, text: str) -> Dict[str, Any]:
        match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
        payload = match.group(1) if match else text
        return json.loads(payload)


    def call_stream_llm(
        self,
        system_prompt: str,
        user_prompt: str,
    ) :
        """
        Attempt Gemini streaming call with a single retry; fall back to OpenAI
        streaming call if Gemini fails.
        """
        delay = self.base_delay
        last_exception: Optional[Exception] = None

        
        
        for attempt in range(self.retries + 1):
            try:
                logger.info("Trying gemini ")
                response, metadata = self.gemini.call_stream_llm(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                )
                   
                logger.info("Metadata: ", metadata)

                
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
            logger.info("Gemini all attempts exhausted. Trying OpenAI")
            openai_response, openai_metadata = self.openai.call_stream_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )

            logger.info("Metadata: ", openai_metadata)

         
            return openai_response
        except Exception as exc:
            if last_exception is not None:
                exc.__cause__ = last_exception  
            raise
