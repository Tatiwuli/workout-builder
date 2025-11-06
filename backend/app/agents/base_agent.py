from abc import ABC, abstractmethod
from ..llms.llm import GeminiLLM
from ..database.mongodb_handler import WorkoutBuilderDatabaseHandler
from datetime import datetime
import os
from dotenv import load_dotenv
import json


class BaseAgent(ABC):
    def __init__(self):

       
        self.db_handler = WorkoutBuilderDatabaseHandler()
        self.llm = GeminiLLM()#model name default gemini 2.5 flash

    def combine_texts(self, texts):
        """
        Combines multiple texts into a structured format.
        """
        return "\n\n### Section ###\n\n".join(map(str, texts))

    
    def _call_llm(self, system_prompt, user_prompt):
        """
       
        """
        try:

            return self.llm.call_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
        except KeyError as e:
            raise ValueError(f"Missing placeholder for substitution: {e}")

    @abstractmethod
    def prepare_wiki_input(self, *args, **kwargs):
        """
        Fetches wiki input. Must be implemented by subclasses.
        """
        pass
