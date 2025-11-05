from abc import ABC, abstractmethod
from ..llms.llm import OpenAILLM
from ..database.mongodb_handler import WorkoutBuilderDatabaseHandler
from datetime import datetime
import os
from dotenv import load_dotenv
import json


class BaseAgent(ABC):
    def __init__(self, database_name="workout_builder", llm_model_name="gpt-5-mini-2025-08-07"):

        load_dotenv()

        self.api_key = os.getenv("OPENAI_API_KEY")
    
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment or passed explicitly.")

        self.mongo_uri = os.getenv("MONGODB_URI")
       
        if not self.mongo_uri:
            raise ValueError(
                "MONGODB_URI not found in environment or passed explicitly.")

        self.db_handler = WorkoutBuilderDatabaseHandler(
            database_name, secrets_mongo_uri=self.mongo_uri)
        self.llm = OpenAILLM(model_name=llm_model_name, api_key=self.api_key)

    def combine_texts(self, texts):
        """
        Combines multiple texts into a structured format.

        Args:
            texts (list): List of text segments.

        Returns:
            str: Combined text.
        """
        return "\n\n### Section ###\n\n".join(map(str, texts))

    def save_output_to_json(self, output_data, file_prefix):
        """
        Saves the GPT output to a JSON file.

        Args:
            output_data (dict): Data to save.
            file_prefix (str): Prefix for the JSON file name.

        Returns:
            str: Path to the saved JSON file.
        """
        # Get absolute path to backend directory (parent of agents directory)
        backend_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        folder_path = os.path.join(
            backend_dir, "data", f"{file_prefix}_json")
        os.makedirs(folder_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = os.path.join(
            folder_path, f"{file_prefix}_{timestamp}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=4)
        return file_path

    def _call_llm(self, prompts, system_input, assistant_input, user_input, **kwargs):
        """
        Executes the LLM call with substituted prompts.
        """
        try:

            system_content = prompts["system_prompt"].substitute(
                system_input=system_input)
            assistant_content = prompts["assistant_prompt"].substitute(
                assistant_input=assistant_input)
            user_content = prompts["user_prompt"].substitute(
                user_input=user_input, **kwargs)

            return self.llm.call_api(
                system_prompt=system_content,
                assistant_prompt=assistant_content,
                user_prompt=user_content,
            )
        except KeyError as e:
            raise ValueError(f"Missing placeholder for substitution: {e}")

    @abstractmethod
    def prepare_assistant_input(self, *args, **kwargs):
        """
        Fetches assistant input. Must be implemented by subclasses.
        """
        pass
