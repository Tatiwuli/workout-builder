from .agents_prompts.exercise_selector_prompts import system_prompt, user_prompt
from ..llms.llm import GeminiLLM
from ..utils.agent_utils import save_output_to_json, combine_texts


class ExerciseSelectorAgent:
    def __init__(self, user_needs: dict, workout_knowledge: dict, llm=None):
        self.user_needs = user_needs
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.llm = llm or GeminiLLM()
        self.workout_knowledge = workout_knowledge

    def run(self):
        print("Preparing wiki input...")
        wiki_input = self.workout_knowledge["fitness_level_wiki"]

        print("Preparing exercises list...")
        exercises_summary = self.workout_knowledge["exercises_summary"]
        main_knowledge_summaries = self.workout_knowledge["main_knowledge_summaries"]
        exercises_list = combine_texts(exercises_summary + main_knowledge_summaries)

        formatted_system_prompt = self.system_prompt.substitute(
            wiki_input=wiki_input
        )

        formatted_user_prompt = self.user_prompt.substitute(
            exercises_list=exercises_list,
            user_needs=self.user_needs
        )

        print("Calling LLM for exercise selection...")
        selected_exercises = self.llm.call_llm(
            system_prompt=formatted_system_prompt,
            user_prompt=formatted_user_prompt
        )

        print("Saving selected exercises to JSON...")
        json_filepath = save_output_to_json(
            selected_exercises, "selected_exercises"
        )
        print(f"Saved to JSON: {json_filepath}")

        print("Exercise selection completed successfully!")
        return selected_exercises
