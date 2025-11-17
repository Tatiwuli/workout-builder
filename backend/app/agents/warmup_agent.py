from .agents_prompts.warmup_agent_prompts import system_prompt, user_prompt
from ..llms.llm_model import LLMService
from ..utils.agent_utils import save_output_to_json, combine_texts
from ..schemas.workouts import WarmupSectionFinal
from typing import Dict, Any, Tuple, Union


class WarmupAgent:
    def __init__(self, workout_plan: dict,stream_response: bool = False):
        self.workout_plan = workout_plan
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.llm = LLMService()
        self.stream_response = stream_response

    def run(self) -> Union[Dict[str, Any], Tuple[Dict[str, Any], Dict[str, Any]]]:

     
        formatted_system_prompt = self.system_prompt.substitute(warmup_duration = 5.0)
        formatted_user_prompt = self.user_prompt.substitute(
            final_workout_plan= self.workout_plan
        )

        print("Calling LLM to generate the warmup plan...")

        if self.stream_response:
            try:
                warmup_output, metadata = self.llm.call_stream_llm(
                    system_prompt=formatted_system_prompt,
                    user_prompt=formatted_user_prompt,
                    response_model=WarmupSectionFinal
                )
                
                # Validate response is not empty
                if not isinstance(warmup_output, dict):
                    raise RuntimeError("Warmup agent returned invalid response type")
                
                if "warmup_exercises" not in warmup_output:
                    raise RuntimeError("Warmup agent response missing 'warmup_exercises' field")
                
                if len(warmup_output.get("warmup_exercises", [])) == 0:
                    raise RuntimeError("Warmup agent returned an empty warmup_exercises list")
                    
            except Exception as e:
                raise RuntimeError(f"Warmup Agent Error: {e}")
        else:
            try:
                warmup_output = self.llm.call_llm(
                    system_prompt=formatted_system_prompt,
                    user_prompt=formatted_user_prompt,
                    response_model=WarmupSectionFinal,
                )
                
                # Validate response is not empty
                if not isinstance(warmup_output, dict):
                    raise RuntimeError("Warmup agent returned invalid response type")
                
                if "warmup_exercises" not in warmup_output:
                    raise RuntimeError("Warmup agent response missing 'warmup_exercises' field")
                
                if len(warmup_output.get("warmup_exercises", [])) == 0:
                    raise RuntimeError("Warmup agent returned an empty warmup_exercises list")
                    
            except Exception as e:
                raise RuntimeError(f"Warmup Agent Error: {e}")

        print("Saving warmup section to JSON...")
        json_filepath = save_output_to_json(
            warmup_output, "warmup_section", 
        )
        print(f"Saved to JSON: {json_filepath}")

        print("Warmup section completed successfully!")
        if self.stream_response:
            metadata = metadata or {}
            metadata.setdefault("stage", "warmup")
            return warmup_output, metadata
        return warmup_output
