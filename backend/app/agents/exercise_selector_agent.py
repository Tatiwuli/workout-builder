from .base_agent import BaseAgent
from .agents_prompts.exercise_selector_prompts import system_prompt, assistant_prompt, user_prompt


class ExerciseSelectorAgent(BaseAgent):
    def __init__(self):

        self.system_prompt = system_prompt
        self.assistant_prompt = assistant_prompt
        self.user_prompt = user_prompt

        super().__init__(llm_model_name="models/gemini-2.5-flash")

    def prepare_assistant_input(self):
        """
        Fetch assistant input from the 'wikis' collection.
        """
        # Fetch wiki data for fitness levels
        wiki_doc = self.db_handler.fetch_data(
            collection_name="wikis", query={"wiki_name": "wiki_by_fitness_level"}
        )
        if not wiki_doc:
            raise ValueError(
                "No document found with wiki_name 'wiki_by_fitness_level'.")

        # Extract fitness levels and their data
        fitness_levels_data = {}
        fitness_levels = wiki_doc[0].get("fitness_levels", {})
        for fitness_level, content in fitness_levels.items():
            fitness_levels_data[fitness_level] = {
                "exercise_selection": content.get("exercise_selection", {}),
                "time_constraints": content.get("time_constraints", {}),
            }

        # Return consolidated assistant input
        return self.combine_texts([fitness_levels_data])

    def prepare_user_input(self, muscle_groups):

        # Fetch documents matching the muscle groups
        documents = self.db_handler.fetch_data(
            collection_name="videos_summaries",
            query={"video_targeted_muscle_groups": {"$in": muscle_groups}},
        )

        # Extract relevant data
        relevant_exercises = [
            doc.get("exercises_summary", {}) for doc in documents if "exercises_summary" in doc
        ]

        main_knowledge_summaries = [
            doc.get("main_knowledge_summary", {}) for doc in documents
        ]

        # Combine data into a single input text
        return self.combine_texts(relevant_exercises + main_knowledge_summaries)

    def run(self, user_needs):
        """
        Runs the ExerciseSelectorAgent with the given user needs.

        Args:
            user_needs (dict): User-specific requirements.

        Returns:
            dict: Selected exercises output.
        """

        print("Fetching assistant input...")
        assistant_input = self.prepare_assistant_input()

        print("Fetching user input...")
        user_input = self.prepare_user_input(user_needs["muscle_groups"])

        prompts = {"system_prompt": self.system_prompt,
                   "assistant_prompt": self.assistant_prompt,
                   "user_prompt": self.user_prompt
                   }

        print("Calling the LLM for exercise selection...")
        selected_exercises = self._call_llm(
            system_input=user_needs,
            assistant_input=assistant_input,
            user_input=user_input,
            prompts=prompts,
        )

        print("Saving selected exercises to JSON...")
        json_filepath = self.save_output_to_json(
            selected_exercises, "selected_exercises")
        print(f"Saved to JSON: {json_filepath}")
        print("response: ", selected_exercises)
        return selected_exercises
