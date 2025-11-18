# from .agents_prompts.personal_trainer_prompts import system_prompt, user_prompt
# from ..llms.llm_model import LLMService
# from ..utils.agent_utils import save_output_to_json, combine_texts
# from ..schemas.workouts import FinalWorkoutPlan
# from typing import Dict, Any, Tuple, Union


# class PersonalTrainerAgent:
#     def __init__(self, workout_knowledge: dict, stream_response: bool = False):
#         self.system_prompt = system_prompt
        
#         self.user_prompt = user_prompt
#         self.llm = LLMService()
#         self.workout_knowledge = workout_knowledge
#         self.stream_response = stream_response

#     def run(self, user_needs, workout_plan, selected_exercises) -> Union[Dict[str, Any], Tuple[Dict[str, Any], Dict[str, Any]]]:
#         print("Preparing assistant input...")
#         main_knowledge_summaries = self.workout_knowledge["main_knowledge_summaries"]
#         wiki_input = combine_texts([selected_exercises, *main_knowledge_summaries])


#         formatted_system_prompt = self.system_prompt.substitute(
#             wiki_input = wiki_input
#         )

#         formatted_user_prompt = self.user_prompt.substitute(
#             workout_plan= workout_plan, user_needs = user_needs
#         )

#         print("Calling LLM to finalize the workout plan...")
#         if self.stream_response:
#             try:
#                 final_workout_plan, metadata = self.llm.call_stream_llm(
#                 system_prompt=formatted_system_prompt,
#                 user_prompt=formatted_user_prompt,
#                 response_model  = FinalWorkoutPlan,
            
#             )
#             except Exception as e :
#                 raise RuntimeError("Personal Trainer Agent Error (Stream): ", e)
#         else:
#             try:
#                 final_workout_plan = self.llm.call_llm(
#                     system_prompt=formatted_system_prompt,
#                     user_prompt=formatted_user_prompt,
#                     response_model=FinalWorkoutPlan,
#                 )
#             except Exception as e :
#                 raise RuntimeError("Personal Trainer Agent Error (Non-Stream): ", e)

#         print("Saving final workout plan to JSON...")
#         json_filepath = save_output_to_json(
#             final_workout_plan, "final_workout_plan")
#         print(f"Saved to JSON: {json_filepath}")

#         if self.stream_response:
#             metadata = metadata or {}
#             metadata.setdefault("stage", "personal_trainer")
#             return final_workout_plan, metadata
#         return final_workout_plan
