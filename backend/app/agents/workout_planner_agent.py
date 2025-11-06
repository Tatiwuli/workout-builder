from .agents_prompts.workout_planner_prompts import system_prompt, user_prompt
from ..llms.llm import GeminiLLM
from ..utils.agent_utils import save_output_to_json, combine_texts


class WorkoutPlannerAgent:
    def __init__(self, user_needs: dict, exercise_selector_output: dict, workout_knowledge: dict, llm=None):
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.llm = llm or GeminiLLM()
        self.user_needs = user_needs
        self.exercise_selector_output = exercise_selector_output
        self.workout_knowledge = workout_knowledge

    def adjust_workout_duration(self):
        """
        Adjusts the workout duration by subtracting the warmup duration.

        Args:
            user_needs (dict): The original user needs with workout duration.
            exercise_selector_output (dict): Output from the ExerciseSelectorAgent.

        Returns:
            dict: Updated user_needs with adjusted workout duration.
        """
        # Extract the original workout duration
        original_duration = int(self.user_needs.get("workout_duration", 0))

        # Extract the warmup duration from the exercise selector output
        warmup_duration = self.exercise_selector_output.get(
            "warmup", {}).get("warmup_total_duration", 0)

        # Calculate the adjusted workout duration
        adjusted_duration = original_duration - warmup_duration

        
        self.user_needs["workout_duration"] = max(
            0, adjusted_duration)  # Ensure duration is not negative
        return self.user_needs

    def run(self):
        """
        Runs the WorkoutPlannerAgent with the given inputs.

        Args:
            user_needs (dict): User-specific requirements.
            exercise_selector_output (dict): Output from ExerciseSelectorAgent.

        Returns:
            dict: Generated workout plan.
        """
        adjusted_user_needs = self.adjust_workout_duration()

        print("Preparing wiki input...")
        fitness_level_wiki = str(self.workout_knowledge["fitness_level_wiki"])
        muscle_group_wiki = str(self.workout_knowledge["muscle_group_wiki"])
        main_knowledge = str(self.workout_knowledge["main_knowledge_summaries"])
        wiki_input = combine_texts([fitness_level_wiki, muscle_group_wiki, main_knowledge])

        print("Preparing exercises list...")
        exercises_list = self.exercise_selector_output.get("exercises", "")

        formatted_system_prompt = self.system_prompt.substitute(
            wiki_input=wiki_input,
            workout_duration=adjusted_user_needs.get("workout_duration", "")
        )

        formatted_user_prompt = self.user_prompt.substitute(
            exercises_list=exercises_list,
            user_needs=adjusted_user_needs
        )

        print("Calling LLM for workout planning...")
        planned_workout = self.llm.call_llm(
            system_prompt=formatted_system_prompt,
            user_prompt=formatted_user_prompt
        )

        print("Saving workout plan to JSON...")
        json_filepath = save_output_to_json(
            planned_workout, "planned_workouts")
        print(f"Saved to JSON: {json_filepath}")

        return planned_workout
