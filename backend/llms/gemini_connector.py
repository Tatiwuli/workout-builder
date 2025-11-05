import json
import os
import re
import logging
from datetime import datetime

from google import genai
from google.genai import types

from ..database.mongodb_handler import WorkoutBuilderDatabaseHandler
from ..app.services.user_response_processor import process_user_responses

from ..agents.agents_prompts.exercise_selector_prompts import (
    system_prompt as ex_sys,
    assistant_prompt as ex_ast,
    user_prompt as ex_usr,
)
from ..agents.agents_prompts.workout_planner_prompts import (
    system_prompt as wp_sys,
    assistant_prompt as wp_ast,
    user_prompt as wp_usr,
)
from ..agents.agents_prompts.personal_trainer_prompts import (
    system_prompt as pt_sys,
    assistant_prompt as pt_ast,
    user_prompt as pt_usr,
)


logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


def _save_json(output_data, file_prefix):
    """
    Save JSON under backend/database/<prefix>_json with timestamped filename.
    """
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder_path = os.path.join(backend_dir, "database", f"{file_prefix}_json")
    os.makedirs(folder_path, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = os.path.join(folder_path, f"{file_prefix}_{timestamp}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)
    return file_path


def _json_from_text(text: str) -> dict:
    """
    Extract JSON object from plain text or fenced code.
    """
    match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
    payload = match.group(1) if match else text
    return json.loads(payload)


class GeminiClient:
    """
    Minimal Gemini client wrapper using the latest google-genai SDK.
    - Requires GOOGLE_API_KEY in environment.
    - Uses system_instruction and a single user content string.
    """

    def __init__(self, model: str = "gemini-2.5-flash", temperature: float = 0.0):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is required in environment")
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def generate_json(self, system_instruction: str, user_content: str) -> dict:
        resp = self.client.models.generate_content(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=self.temperature,
            ),
            contents=user_content,
        )
        text = getattr(resp, "text", None) or ""
        if not text:
            # Fallback to first candidate text if available
            try:
                text = resp.candidates[0].content.parts[0].text
            except Exception:
                pass
        if not text:
            raise RuntimeError("Empty response from Gemini")
        try:
            return _json_from_text(text.strip())
        except Exception as e:
            raise RuntimeError(f"Failed to parse JSON from Gemini: {e}\nRaw: {text[:400]}...")


class GeminiWorkflow:
    """
    Reproduces the Exercise Selector -> Workout Planner -> Personal Trainer
    workflow using Gemini, existing prompts, and Mongo-backed data.
    """

    def __init__(self, database_name: str = "workout_builder", model: str = "gemini-2.5-flash", temperature: float = 0.0):
        self.db = WorkoutBuilderDatabaseHandler(database_name)
        self.gemini = GeminiClient(model=model, temperature=temperature)

    @staticmethod
    def _combine_texts(texts):
        return "\n\n### Section ###\n\n".join(map(str, texts))

    # --------- Stage 1: Exercise Selector ---------
    def _ex_selector_assistant_input(self):
        wiki_doc = self.db.fetch_data(collection_name="wikis", query={"wiki_name": "wiki_by_fitness_level"})
        if not wiki_doc:
            raise ValueError("No document found with wiki_name 'wiki_by_fitness_level'.")
        fitness_levels_data = {}
        fitness_levels = wiki_doc[0].get("fitness_levels", {})
        for fitness_level, content in fitness_levels.items():
            fitness_levels_data[fitness_level] = {
                "exercise_selection": content.get("exercise_selection", {}),
                "time_constraints": content.get("time_constraints", {}),
            }
        return self._combine_texts([fitness_levels_data])

    def _ex_selector_user_input(self, muscle_groups):
        documents = self.db.fetch_data(collection_name="videos_summaries", query={"video_targeted_muscle_groups": {"$in": muscle_groups}})
        relevant_exercises = [doc.get("exercises_summary", {}) for doc in documents if "exercises_summary" in doc]
        main_knowledge_summaries = [doc.get("main_knowledge_summary", {}) for doc in documents]
        return self._combine_texts(relevant_exercises + main_knowledge_summaries)

    def run_exercise_selector(self, user_needs: dict) -> dict:
        logger.info("[Stage 1] Exercise selection")
        system_text = ex_sys.substitute(system_input=user_needs)
        assistant_text = ex_ast.substitute(assistant_input=self._ex_selector_assistant_input())
        user_text = ex_usr.substitute(user_input=self._ex_selector_user_input(user_needs["muscle_groups"]))
        result = self.gemini.generate_json(system_instruction=f"{system_text}\n\n{assistant_text}", user_content=user_text)
        _save_json(result, "selected_exercises")
        return result

    # --------- Stage 2: Workout Planner ---------
    def _wp_assistant_input(self, muscle_groups):
        wiki_fit = self.db.fetch_data(collection_name="wikis", query={"wiki_name": "wiki_by_fitness_level"})
        if not wiki_fit:
            raise ValueError("No document found with wiki_name 'wiki_by_fitness_level'.")
        wiki_muscle = self.db.fetch_data(collection_name="wikis", query={"wiki_name": "wiki_by_muscle_group"})
        if not wiki_muscle:
            raise ValueError("No document found with wiki_name 'wiki_by_muscle_group'.")
        key_principles = {}
        for mg in muscle_groups:
            matching = [s for s in wiki_muscle[0].get("sections", []) if mg in s.get("muscle_groups", [])]
            key_principles[mg] = {"key_principles": wiki_muscle[0].get("key_principles", []), "sections": matching}
        video_docs = self.db.fetch_data(collection_name="videos_summaries", query={"video_targeted_muscle_groups": {"$in": muscle_groups}})
        main_knowledge = [doc.get("main_knowledge_summary", {}) for doc in video_docs]
        return self._combine_texts([str(wiki_fit), str(key_principles), str(main_knowledge)])

    @staticmethod
    def _adjust_duration(user_needs: dict, exercise_selector_output: dict) -> dict:
        original = int(user_needs.get("workout_duration", 0))
        warmup = exercise_selector_output.get("warmup", {})
        warmup_duration = warmup.get("warmup_total_duration") or warmup.get("total_warmup_duration") or 0
        user_needs["workout_duration"] = max(0, original - int(warmup_duration))
        return user_needs

    def run_workout_planner(self, user_needs: dict, exercise_selector_output: dict) -> dict:
        logger.info("[Stage 2] Workout planning")
        adjusted = self._adjust_duration(dict(user_needs), exercise_selector_output)
        system_text = wp_sys.substitute(system_input=adjusted)
        assistant_text = wp_ast.substitute(assistant_input=self._wp_assistant_input(adjusted["muscle_groups"]))
        user_text = wp_usr.substitute(user_input=exercise_selector_output.get("exercises"), workout_duration=adjusted.get("workout_duration"))
        result = self.gemini.generate_json(system_instruction=f"{system_text}\n\n{assistant_text}", user_content=user_text)
        _save_json(result, "planned_workouts")
        return result

    # --------- Stage 3: Personal Trainer ---------
    def _pt_assistant_input(self, selected_exercises: dict, muscle_groups):
        video_docs = self.db.fetch_data(collection_name="videos_summaries", query={"video_targeted_muscle_groups": {"$in": muscle_groups}})
        main_knowledge = [doc.get("main_knowledge_summary", {}) for doc in video_docs]
        return self._combine_texts([selected_exercises, *main_knowledge])

    def run_personal_trainer(self, user_needs: dict, workout_plan_draft: dict, selected_exercises: dict) -> dict:
        logger.info("[Stage 3] Finalizing workout plan")
        system_text = pt_sys.substitute(system_input=user_needs)
        assistant_text = pt_ast.substitute(assistant_input=self._pt_assistant_input(selected_exercises, user_needs["muscle_groups"]))
        user_text = pt_usr.substitute(user_input=workout_plan_draft)
        result = self.gemini.generate_json(system_instruction=f"{system_text}\n\n{assistant_text}", user_content=user_text)
        _save_json(result, "final_workout_plan")
        return result

    # --------- Public entrypoint ---------
    def run_full_workflow(self, raw_user_data: dict) -> dict:
        """
        Accept questionnaire-style raw input and return final workout plan.
        """
        logger.info("Processing user responses")
        processed = process_user_responses(raw_user_data)
        selected = self.run_exercise_selector(processed)
        planned = self.run_workout_planner(processed, selected)
        final = self.run_personal_trainer(processed, planned, selected)
        return final


