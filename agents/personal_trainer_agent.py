from agents.base_agent import BaseAgent
from agents.agents_prompts.personal_trainer_prompts import system_prompt, assistant_prompt, user_prompt


class PersonalTrainerAgent(BaseAgent):
    def __init__(self,api_key = None):
        if not api_key:
            raise ValueError(
                "API key is required to initialize the PersonalTrainerAgent.")
        self.system_prompt = system_prompt
        self.assistant_prompt = assistant_prompt
        self.user_prompt = user_prompt

        super().__init__(
            api_key=api_key, llm_model_name="gpt-4o"
        )

    def prepare_assistant_input(self, selected_exercises, muscle_groups):
        """
        Fetches assistant input by combining selected exercises and main knowledge summaries.

        Args:
            selected_exercises (dict): Exercises selected from the ExerciseSelectorAgent.
            muscle_groups (list): List of targeted muscle groups.

        Returns:
            str: Consolidated assistant input text.
        """
        # Fetch documents for targeted muscle groups
        video_documents = self.db_handler.fetch_data(
            collection_name="videos_summaries",
            query={"video_targeted_muscle_groups": {"$in": muscle_groups}},
        )

        # Extract main knowledge summaries
        main_knowledge_summaries = [
            doc.get("main_knowledge_summary", {}) for doc in video_documents
        ]

        # Combine selected exercises and main knowledge summaries
        texts_list = [selected_exercises, *main_knowledge_summaries]
        return self.combine_texts(texts_list)

    def run(self, user_needs, workout_plan_draft, selected_exercises):
        """
        Runs the PersonalTrainerAgent with the given inputs.

        Args:
            user_needs (dict): User-specific requirements.
            workout_plan_draft (dict): Draft workout plan from the WorkoutPlannerAgent.
            selected_exercises (dict): Selected exercises from the ExerciseSelectorAgent.

        Returns:
            dict: Finalized workout plan.
        """
        # Fetch assistant input
        print("Fetching assistant input...")
        assistant_input = self.prepare_assistant_input(
            selected_exercises=selected_exercises, muscle_groups=user_needs["muscle_groups"]
        )

        # Prepare user input
        print("Fetching user input...")
        user_input = workout_plan_draft

        # Prepare LLM prompts
        prompts = {"system_prompt": self.system_prompt,
                   "assistant_prompt": self.assistant_prompt,
                   "user_prompt": self.user_prompt
                   }

        # Call the LLM
        print("Calling the LLM to finalize the workout plan...")
        final_workout_plan = self._call_llm(
            system_input=user_needs,
            assistant_input=assistant_input,
            user_input=user_input,
            prompts=prompts,
        )

        # Save the output
        print("Saving final workout plan to JSON...")
        json_filepath = self.save_output_to_json(
            final_workout_plan, "final_workout_plan")
        print(f"Saved to JSON: {json_filepath}")

        return final_workout_plan
