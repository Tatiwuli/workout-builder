from .agents_prompts.personal_trainer_prompts import system_prompt, user_prompt
from ..llms.llm import GeminiLLM
from ..utils.agent_utils import save_output_to_json, combine_texts


class PersonalTrainerAgent:
    def __init__(self, workout_knowledge: dict, llm=None):
        self.system_prompt = system_prompt
        
        self.user_prompt = user_prompt
        self.llm = llm or GeminiLLM()
        self.workout_knowledge = workout_knowledge

    def run(self, user_needs, workout_plan, selected_exercises):
        print("Preparing assistant input...")
        main_knowledge_summaries = self.workout_knowledge["main_knowledge_summaries"]
        wiki_input = combine_texts([selected_exercises, *main_knowledge_summaries])


        formatted_system_prompt = self.system_prompt.substitute(
            wiki_input = wiki_input
        )

        formatted_user_prompt = self.user_prompt.substitute(
            workout_plan= workout_plan, user_needs = user_needs
        )

        print("Calling LLM to finalize the workout plan...")
        final_workout_plan = self.llm.call_llm(
            system_prompt=formatted_system_prompt,
            user_prompt=formatted_user_prompt
        )

        print("Saving final workout plan to JSON...")
        json_filepath = save_output_to_json(
            final_workout_plan, "final_workout_plan")
        print(f"Saved to JSON: {json_filepath}")

        return final_workout_plan
