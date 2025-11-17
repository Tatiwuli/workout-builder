from .agents_prompts.workout_planner_prompts import system_prompt, user_prompt
from ..llms.llm_model import LLMService
from ..utils.agent_utils import save_output_to_json, combine_texts
from ..schemas.workouts import WorkoutPlannerOutput
from typing import Dict, Any, Tuple, Union


class WorkoutPlannerAgent:
    def __init__(self, user_needs: dict, exercise_selector_output: dict, workout_knowledge: dict, stream_response: bool = False):
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.llm = LLMService()
        self.user_needs = user_needs
        self.exercise_selector_output = exercise_selector_output
        self.workout_knowledge = workout_knowledge
        self.stream_response = stream_response


    def run(self, warmup_duration) -> Union[Dict[str, Any], Tuple[Dict[str, Any], Dict[str, Any]]]:
        """
        Runs the WorkoutPlannerAgent with the given inputs.

        Args:
            user_needs (dict): User-specific requirements.
            exercise_selector_output (dict): Output from ExerciseSelectorAgent.

        Returns:
            dict: Generated workout plan.
        """


        self.user_needs["workout_duration"] = self.user_needs["workout_duration"] - warmup_duration

        print("Preparing wiki input...")
        fitness_level_wiki = str(self.workout_knowledge["fitness_level_wiki"])
        muscle_group_wiki = str(self.workout_knowledge["muscle_group_wiki"])
        main_knowledge = str(self.workout_knowledge["main_knowledge_summaries"])
        wiki_input = combine_texts([fitness_level_wiki, muscle_group_wiki, main_knowledge])

        print("Preparing exercises list...")
        exercises_list = self.exercise_selector_output.get("exercises", "")

        formatted_system_prompt = self.system_prompt.substitute(
            wiki_input=wiki_input,
            workout_duration=self.user_needs.get("workout_duration", "")
        )

        formatted_user_prompt = self.user_prompt.substitute(
            exercises_list=exercises_list,
            user_needs= self.user_needs
        )

        print("Calling LLM for workout planning...")
        if self.stream_response:
            try:
                planned_workout, metadata = self.llm.call_stream_llm(
                    system_prompt=formatted_system_prompt,
                    user_prompt=formatted_user_prompt,
                    response_model=WorkoutPlannerOutput
                )
                
                # Validate response is not empty
                if not isinstance(planned_workout, dict):
                    raise RuntimeError("Workout Planner agent returned invalid response type")
                
                if "sets" not in planned_workout:
                    raise RuntimeError("Workout Planner agent response missing 'sets' field")
                
                if len(planned_workout.get("sets", [])) == 0:
                    raise RuntimeError("Workout Planner agent returned an empty sets list")
                    
            except Exception as e:
                raise RuntimeError(f"Workout Planner Agent Error (Stream): {e}")

        else:
            try:
                planned_workout = self.llm.call_llm(
                    system_prompt=formatted_system_prompt,
                    user_prompt=formatted_user_prompt,
                    response_model=WorkoutPlannerOutput,
                )
                
                # Validate response is not empty
                if not isinstance(planned_workout, dict):
                    raise RuntimeError("Workout Planner agent returned invalid response type")
                
                if "sets" not in planned_workout:
                    raise RuntimeError("Workout Planner agent response missing 'sets' field")
                
                if len(planned_workout.get("sets", [])) == 0:
                    raise RuntimeError("Workout Planner agent returned an empty sets list")
                    
            except Exception as e:
                raise RuntimeError(f"Workout Planner Agent Error (Non-Stream): {e}")


        print("Saving workout plan to JSON...")
        json_filepath = save_output_to_json(
            planned_workout, "planned_workouts")
        print(f"Saved to JSON: {json_filepath}")

        if self.stream_response:
            metadata = metadata or {}
            metadata.setdefault("stage", "workout_planner")
            return planned_workout, metadata
        return planned_workout
