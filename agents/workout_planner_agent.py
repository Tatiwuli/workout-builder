from base_agent import BaseAgent
from agents_prompts.workout_planner_prompts import system_prompt, assistant_prompt, user_prompt


class WorkoutPlannerAgent(BaseAgent):
    def __init__(self):
        self.system_prompt = system_prompt
        self.assistant_prompt = assistant_prompt
        self.user_prompt = user_prompt

        super().__init__(
            llm_model_name="gpt-4o"
        )

    def prepare_assistant_input(self, muscle_groups):
        """
        Fetches assistant input by combining fitness level wiki data,
        muscle group wiki data, and main knowledge summaries.

        Args:
            muscle_groups (list): List of targeted muscle groups.

        Returns:
            str: Consolidated assistant input text.
        """
        # Fetch fitness level wiki
        wiki_fitness_level_doc = self.db_handler.fetch_data(
            collection_name="wikis", query={"wiki_name": "wiki_by_fitness_level"}
        )
        if not wiki_fitness_level_doc:
            raise ValueError(
                "No document found with wiki_name 'wiki_by_fitness_level'.")

        # Fetch muscle group wiki
        wiki_muscle_group_doc = self.db_handler.fetch_data(
            collection_name="wikis", query={"wiki_name": "wiki_by_muscle_group"}
        )
        if not wiki_muscle_group_doc:
            raise ValueError(
                "No document found with wiki_name 'wiki_by_muscle_group'.")

        # Extract relevant sections for targeted muscle groups
        key_principles = {}
        for muscle_group in muscle_groups:
            matching_sections = [
                section for section in wiki_muscle_group_doc[0].get("sections", [])
                if muscle_group in section.get("muscle_groups", [])
            ]
            key_principles[muscle_group] = {
                "key_principles": wiki_muscle_group_doc[0].get("key_principles", []),
                "sections": matching_sections,
            }

        # Fetch main knowledge summaries for videos
        video_documents = self.db_handler.fetch_data(
            collection_name="videos_summaries",
            query={"video_targeted_muscle_groups": {"$in": muscle_groups}},
        )
        main_knowledge_summaries = [
            doc.get("main_knowledge_summary", {}) for doc in video_documents
        ]

        # Combine all inputs into a single text
        texts_list = [
            str(wiki_fitness_level_doc),
            str(key_principles),
            str(main_knowledge_summaries),
        ]
        return self.combine_texts(texts_list)

    def adjust_workout_duration(self, user_needs, exercise_selector_output):
        """
        Adjusts the workout duration by subtracting the warmup duration.

        Args:
            user_needs (dict): The original user needs with workout duration.
            exercise_selector_output (dict): Output from the ExerciseSelectorAgent.

        Returns:
            dict: Updated user_needs with adjusted workout duration.
        """
        # Extract the original workout duration
        original_duration = int(user_needs.get("workout_duration", 0))

        # Extract the warmup duration from the exercise selector output
        warmup_duration = exercise_selector_output.get(
            "warmup", {}).get("warmup_total_duration", 0)

        # Calculate the adjusted workout duration
        adjusted_duration = original_duration - warmup_duration

        # Update the user_needs dictionary
        user_needs["workout_duration"] = max(
            0, adjusted_duration)  # Ensure duration is not negative
        return user_needs

    def run(self, user_needs, exercise_selector_output):
        """
        Runs the WorkoutPlannerAgent with the given inputs.

        Args:
            user_needs (dict): User-specific requirements.
            exercise_selector_output (dict): Output from ExerciseSelectorAgent.

        Returns:
            dict: Generated workout plan.
        """
        # Adjust workout duration by subtracting warmup time
        adjusted_user_needs = self.adjust_workout_duration(
            user_needs, exercise_selector_output)

        # Fetch assistant input
        print("Fetching assistant input...")
        assistant_input = self.prepare_assistant_input(
            adjusted_user_needs["muscle_groups"])

        # Fetch user input (exercises from ExerciseSelector output)
        print("Fetching user input...")
        user_input = exercise_selector_output.get("exercises")

        # Prepare LLM prompts
        # Prepare LLM prompts
        prompts = {"system_prompt": self.system_prompt,
            "assistant_prompt": self.assistant_prompt,
            "user_prompt": self.user_prompt
        }

        # Call the LLM
        print("Calling the LLM for workout planning...")
        planned_workout = self._call_llm(
            prompts=prompts,
            system_input=adjusted_user_needs,
            assistant_input=assistant_input,
            user_input=user_input,
            workout_duration=adjusted_user_needs.get("workout_duration"),
            
        )

        # Save the output
        print("Saving workout plan to JSON...")
        json_filepath = self.save_output_to_json(
            planned_workout, "planned_workouts")
        print(f"Saved to JSON: {json_filepath}")

        return planned_workout
