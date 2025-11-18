from .agents_prompts.workout_planner_prompts import system_prompt, user_prompt
from ..llms.llm_model import LLMService
from ..utils.agent_utils import save_output_to_json, combine_texts, generate_cache_key
from ..schemas.workouts import WorkoutPlannerOutput
from typing import Dict, Any, Tuple, Union


class WorkoutPlannerAgent:
    def __init__(self,  workout_duration: float, exercise_selector_output: dict, shared_prefix: str, stream_response: bool = False):
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.llm = LLMService()
        self.workout_duration = workout_duration
      
        self.exercise_selector_output = exercise_selector_output
        self.shared_prefix = shared_prefix
        self.stream_response = stream_response


    def run(self) -> Union[Dict[str, Any], Tuple[Dict[str, Any], Dict[str, Any]]]:
        """
        Runs the WorkoutPlannerAgent with the given inputs.


        Returns:
            dict: Generated workout plan.
        """


    
        print("Preparing exercises list...")
        exercises_list = self.exercise_selector_output.get("exercises", "")

        # Substitute the template variable first
        substituted_prompt = self.system_prompt.substitute(
            workout_duration=self.workout_duration
        )
        # Prepend shared_prefix at the beginning for OpenAI caching
        # The shared_prefix must come FIRST for caching to work effectively
        formatted_system_prompt = self.shared_prefix + substituted_prompt 

        formatted_user_prompt = self.user_prompt.substitute(
            exercises_list=exercises_list,
        )

        # Generate cache key from shared_prefix for OpenAI caching
        cache_key = generate_cache_key(self.shared_prefix)

        print("Calling LLM for workout planning...")
        if self.stream_response:
            try:
                planned_workout, metadata = self.llm.call_stream_llm(
                    system_prompt=formatted_system_prompt,
                    user_prompt=formatted_user_prompt,
                    response_model=WorkoutPlannerOutput,
                    prompt_cache_key=cache_key
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
                    prompt_cache_key=cache_key
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
