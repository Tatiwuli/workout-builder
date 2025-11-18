from .agents_prompts.exercise_selector_prompts import system_prompt, user_prompt
from ..llms.llm_model import LLMService
from ..utils.agent_utils import save_output_to_json, combine_texts, generate_cache_key
from ..schemas.workouts import ExerciseSelectorOutput
from typing import Dict, Any, Tuple, Union


class ExerciseSelectorAgent:
    def __init__(self, exercises_data: dict,shared_prefix : str, stream_response: bool = False):
    
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.llm = LLMService()
        self.exercises_data = exercises_data
        self.stream_response = stream_response
        self.shared_prefix = shared_prefix
        

    def run(self) -> Union[Dict[str, Any], Tuple[Dict[str, Any], Dict[str, Any]]]:
       
        print("Preparing exercises list...")

        # Get the system prompt template as string and prepend shared_prefix for caching
        formatted_system_prompt = self.shared_prefix + self.system_prompt.template

        formatted_user_prompt = self.user_prompt.substitute(
            exercises_data= self.exercises_data
        )

        # Generate cache key from shared_prefix for OpenAI caching
        cache_key = generate_cache_key(self.shared_prefix)

        print("Calling LLM for exercise selection...")

        if self.stream_response:
            try:
                selected_exercises, metadata = self.llm.call_stream_llm(
                    system_prompt=formatted_system_prompt,
                    user_prompt=formatted_user_prompt,
                    response_model=ExerciseSelectorOutput,
                    prompt_cache_key=cache_key
                )
                
                # Validate response is not empty
                if not isinstance(selected_exercises, dict):
                    raise RuntimeError("Exercise Selector agent returned invalid response type")
                
                if "exercises" not in selected_exercises:
                    raise RuntimeError("Exercise Selector agent response missing 'exercises' field")
                
                if len(selected_exercises.get("exercises", [])) == 0:
                    raise RuntimeError("Exercise Selector agent returned an empty exercises list")
                    
            except Exception as e:
                raise RuntimeError(f"Exercise Selector Agent Error: {e}")
        else:
            try:
                selected_exercises = self.llm.call_llm(
                    system_prompt=formatted_system_prompt,
                    user_prompt=formatted_user_prompt,
                    response_model=ExerciseSelectorOutput,
                    prompt_cache_key=cache_key
                )
                
                # Validate response is not empty
                if not isinstance(selected_exercises, dict):
                    raise RuntimeError("Exercise Selector agent returned invalid response type")
                
                if "exercises" not in selected_exercises:
                    raise RuntimeError("Exercise Selector agent response missing 'exercises' field")
                
                if len(selected_exercises.get("exercises", [])) == 0:
                    raise RuntimeError("Exercise Selector agent returned an empty exercises list")
                    
            except Exception as e:
                raise RuntimeError(f"Exercise Selector Agent Error: {e}")

        print("Saving selected exercises to JSON...")
        json_filepath = save_output_to_json(
            selected_exercises, "selected_exercises", 
        )
        print(f"Saved to JSON: {json_filepath}")

        print("Exercise selection completed successfully!")
        if self.stream_response:
            metadata = metadata or {}
            metadata.setdefault("stage", "exercise_selector")
            return selected_exercises, metadata
        return selected_exercises
