import json
from .exercise_selector_agent import ExerciseSelectorAgent
from .workout_planner_agent import WorkoutPlannerAgent
from .warmup_agent import WarmupAgent
from ..services.workout_knowledge_fetch import WorkoutKnowledgeFetch
from ..utils.agent_utils import combine_texts

from typing import Dict, Any, Union, Tuple, List


class WorkoutBuilderWorkflow:
    def __init__(self, database_name="workout_builder", progress_callback=None, stream_response: bool = False):
    
        self.knowledge_fetch = WorkoutKnowledgeFetch()
        self.progress_callback = progress_callback
        self.stream_response = stream_response
        
    
    def fetch_workout_knowledge(self, user_needs):


        muscle_groups = user_needs["muscle_groups"]
        fitness_level = user_needs.get("fitness_level", "beginners")
        time_constraint = user_needs.get("time_constraint", "medium")

        exercises_summary = self.knowledge_fetch.extract_exercises_summary(muscle_groups)
        main_knowledge_summaries = self.knowledge_fetch.extract_main_knowledge_summary(muscle_groups)
        fitness_level_wiki = self.knowledge_fetch.fetch_fitness_level_wiki(fitness_level, time_constraint)
        
        muscle_group_wiki = self.knowledge_fetch.fetch_muscle_group_wiki(muscle_groups)

        return {
            "exercises_summary": exercises_summary,
            "main_knowledge_summaries": main_knowledge_summaries,
            "fitness_level_wiki": fitness_level_wiki,
            "muscle_group_wiki": muscle_group_wiki
        }

    def compile_final_plan(
        self,
        exercise_selector_output: Dict[str, Any],
        workout_planner_output: Dict[str, Any],
        user_needs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compiles the final workout plan by merging ExerciseSelector and WorkoutPlanner outputs.
        
        Args:
            exercise_selector_output: Output from ExerciseSelectorAgent
            workout_planner_output: Output from WorkoutPlannerAgent
            user_needs: User requirements dictionary
            
        Returns:
            Dict representing the final workout plan (WorkoutPlanWithoutWarmup format)
        """

        #Extract each agent's output exercises section
        selector_exercises = exercise_selector_output.get("exercises", [])
        planner_sets = workout_planner_output.get("sets", [])
       
        # Create a lookup dictionary for exercise selector data by exercise_name to speed up the merging process of the outputs later
        exercise_lookup: Dict[str, Dict[str, Any]] = {}
        for ex in selector_exercises:
            ex_name = ex.get("exercise_name", "")
            exercise_lookup[ex_name] = ex
        
        # Helper function to convert setup/execution to List[str] format
        def normalize_setup_execution(value: Any) -> List[str]:
            """
            Convert setup/execution to Union[str, List[str]] format.
            
            Examples:
            - Input: ["1. Step one", "2. Step two"] -> Output: ["1. Step one", "2. Step two"] (list)
            - Input: '["1. Step one", "2. Step two"]' -> Output: ["1. Step one", "2. Step two"] (parsed JSON string)
            - Input: "Simple string instruction" -> Output: ["Simple string instruction"]
            - Input: "" or None -> Output: []
            """
            if isinstance(value, list):
                return value
            elif isinstance(value, str):
                # If it's a string, check if it looks like a list representation
                if value.strip().startswith('['):
                    # Try to parse it as a list
                    try:
                        parsed = json.loads(value)
                        if isinstance(parsed, list):
                            return parsed
                    except (json.JSONDecodeError, ValueError):
                        pass
                # If it's a non-empty string, convert to list with single item
                if value.strip():
                    return [value]
                return []
            elif value is None:
                return []
            else:
                # Convert other types to list with string representation
                return [str(value)]
        
        # Convert planned sets to final workout sets
        final_sets: List[Dict[str, Any]] = []
        total_duration = 0.0
        unique_exercises = set()
        
        for planned_set in planner_sets:
            # Extract set data
            set_number = planned_set.get("set_number", 0)
            set_duration = planned_set.get("set_duration", 0.0)
            set_strategy = planned_set.get("set_strategy", "")
            set_rest_time = planned_set.get("set_rest_time", 0.0)
            num_rounds = planned_set.get("num_rounds", 0)
            target_muscle_group = planned_set.get("target_muscle_group", [])
            planned_exercises = planned_set.get("exercises", [])
            
            total_duration += set_duration
            
            # Convert exercises in this set
            final_exercises: List[Dict[str, Any]] = []
            
            for planned_ex in planned_exercises:
                # Extract planned exercise data
                ex_name = planned_ex.get("exercise_name", "")
                reps = planned_ex.get("reps", "")
                weight = planned_ex.get("weight", "")
                alternative_exercise = planned_ex.get("alternative_exercise", "")
                alternative_exercise_reps = planned_ex.get("alternative_exercise_reps", "")
                alternative_exercise_weight = planned_ex.get("alternative_exercise_weight", "")
                
                unique_exercises.add(ex_name)
                
                # Get exercise data from selector output (contains setup, execution, media_url, etc.)
                ex_data = exercise_lookup.get(ex_name, {})
                
                # Get target_muscle_parts directly from exercise selector (already in final format)
                # Format: [{"muscle_group": "Back", "muscle_part": ["Lats", "Upper Traps"]}]
                target_muscle_part_list = ex_data.get("target_muscle_parts", [])
                
                # Fallback: if target_muscle_parts is missing, create from targeted_muscle_groups
                if not target_muscle_part_list:
                    targeted_muscle_groups = ex_data.get("targeted_muscle_groups", []) or ex_data.get("target_muscles", [])
                    target_muscle_part_list = [
                        {"muscle_group": group, "muscle_part": []}
                        for group in targeted_muscle_groups
                    ]
                
                # Handle alternative exercise - get name and data
                alternative_ex_name = alternative_exercise if alternative_exercise else ex_data.get("alternative_exercise", "")
                
                
                alternative_exercise_setup = ex_data.get("alternative_exercise_setup", [])
                alternative_exercise_execution = ex_data.get("alternative_exercise_execution", [])
                
        
                
                # Get alternative exercise media URL
                alternative_exercise_media_url = ex_data.get("alternative_exercise_media_url", "")
            

                #Merging into the final exercise object
                final_exercise = {
                    "exercise_name": ex_name,
                    "target_muscle_part": target_muscle_part_list,
                    "setup": normalize_setup_execution(ex_data.get("setup", "")),
                    "execution": normalize_setup_execution(ex_data.get("execution", "")),
                    "media_url": ex_data.get("media_url", ""),
                    "reps": reps,
                    "weight": weight,
                    
                    "alternative_exercise": alternative_ex_name,
                    "alternative_exercise_setup": normalize_setup_execution(alternative_exercise_setup),
                    "alternative_exercise_execution": normalize_setup_execution(alternative_exercise_execution),
                    "alternative_exercise_media_url": alternative_exercise_media_url,
                    "alternative_exercise_reps": alternative_exercise_reps,
                    "alternative_exercise_weight": alternative_exercise_weight,
                    "additional_tips": ex_data.get("additional_notes", ""),
                }
                
                final_exercises.append(final_exercise)
            
            # Build final set (set metadata first, then exercises)
            final_set = {
                "set_number": set_number,
                "set_strategy": set_strategy,
                "set_duration": set_duration,
                "set_rest_time": set_rest_time,
                "num_rounds": num_rounds,
                "target_muscle_group": target_muscle_group,
                "exercises": final_exercises,
            }
            
            final_sets.append(final_set)
        
        # Generate workout title based on muscle groups
        muscle_groups = user_needs.get("muscle_groups", [])
        fitness_level = user_needs.get("fitness_level", "beginners")
        # Format fitness level for display
        fitness_level_display = fitness_level.replace("_", " ").title()
        if muscle_groups:
            muscle_groups_str = " & ".join([mg.title() for mg in muscle_groups])
            workout_title = f"{muscle_groups_str} Workout - {fitness_level_display}"
        else:
            workout_title = f"Workout Plan - {fitness_level_display}"
        
        # Build final workout plan
        final_plan = {
            "workout_title": workout_title,
            "total_workout_duration": total_duration,
            "num_exercises": len(unique_exercises),
            "sets": final_sets,
        }
        
        return final_plan

    def compile_final_plan_warmup(
        self,
        final_plan: Dict[str, Any],
        warmup_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compiles the final workout plan by combining the workout plan and warmup section.
        
        Args:
            final_plan: Output from compile_final_plan (WorkoutPlanWithoutWarmup format)
            warmup_output: Output from WarmupAgent (WarmupSectionFinal format)
            
        Returns:
            Dict representing the final workout plan (FinalWorkoutPlan format)
        """
        # Extract data from final_plan
        workout_title = final_plan.get("workout_title", "")
        total_workout_duration = final_plan.get("total_workout_duration", 0.0)
        num_exercises = final_plan.get("num_exercises", 0)
        sets = final_plan.get("sets", [])
        
        # Extract warmup section from warmup_output
        warmup_section = {
            "total_warmup_duration": warmup_output.get("total_warmup_duration", 0.0),
            "warmup_exercises": warmup_output.get("warmup_exercises", [])
        }
        
        # Compile final workout plan with warmup
        final_workout_plan = {
            "workout_title": workout_title,
            "total_workout_duration": total_workout_duration,
            "num_exercises": num_exercises,
            "warmup": warmup_section,
            "sets": sets,
        }
        
        return final_workout_plan

    def run_workflow(self, processed_responses: Dict[str, Any]) -> Union[Dict[str, Any], Tuple[Dict[str, Any], List[Dict[str, Any]]]]:
        if self.progress_callback:
            self.progress_callback("Starting Workflow 🚀", 0)

        if self.progress_callback:
            self.progress_callback("Fetching common data...", 10)

        workout_knowledge = self.fetch_workout_knowledge(processed_responses)

        metadata_records: List[Dict[str, Any]] = []

        if self.progress_callback:
            self.progress_callback("Selecting Exercises 🏋️", 20)

        wiki_input = combine_texts([
            workout_knowledge['fitness_level_wiki'], 
            workout_knowledge['muscle_group_wiki'], 
            workout_knowledge['main_knowledge_summaries']
        ])
      

        # Format processed_responses as JSON for consistent string representation
        # This ensures the shared_prefix is identical for caching when user data is the same
        user_needs_json = json.dumps(processed_responses, sort_keys=True, indent=2)
        
        shared_prefix = f"""
## Goal
You are a personal trainer experienced with designing workout session to meet the client's workout goals and their physical conditions. 

## Hypertrophy Training Wiki Database
The following wiki contains the exercise information and training principles you need to reference:

'''
{wiki_input}
'''

## User needs
The following object contains the user's workout goals and physical needs. Your decisions must always aim to meet the user's needs. 

{user_needs_json}
"""
        
        exercise_selector = ExerciseSelectorAgent(
                exercises_data=workout_knowledge['exercises_summary'],
                shared_prefix = shared_prefix,
                stream_response=self.stream_response,
            )
        if self.stream_response:
            exercise_selector_output,metadata_exercise_selector = exercise_selector.run()
        else: 
            exercise_selector_output = exercise_selector.run()


        if self.progress_callback:
            self.progress_callback("Structuring Workout 📋", 50)
        
        # Calculate workout duration minus warmup time (5 minutes)
        warmup_duration = 5.0
        adjusted_workout_duration = processed_responses.get('workout_duration', 0) - warmup_duration
        
        workout_planner = WorkoutPlannerAgent(
            adjusted_workout_duration,
            exercise_selector_output,
            shared_prefix=shared_prefix,
            stream_response=self.stream_response,
        )
        if self.stream_response:
            workout_planner_output, metadata_workout_planner = workout_planner.run()
        else: 
            workout_planner_output = workout_planner.run()

        if self.progress_callback:
            self.progress_callback("Compiling Final Workout Plan 📝", 80)
        
        # Compile final plan from exercise selector and workout planner outputs
        final_plan = self.compile_final_plan(
            exercise_selector_output=exercise_selector_output,
            workout_planner_output=workout_planner_output,
            user_needs=processed_responses
        )

        if self.progress_callback:
            self.progress_callback("Generating Warmup Section 🔥", 90)

        # Generate warmup section based on final plan
        warmup_agent = WarmupAgent(
            workout_plan=final_plan,
            stream_response=self.stream_response,
        )
        if self.stream_response:
            warmup_output, metadata_warmup = warmup_agent.run()
        else:
            warmup_output = warmup_agent.run()

        if self.progress_callback:
            self.progress_callback("Compiling Final Workout Plan with Warmup 📝", 95)

        # Compile final plan with warmup section
        final_workout_plan = self.compile_final_plan_warmup(
            final_plan=final_plan,
            warmup_output=warmup_output
        )

        if self.progress_callback:
            self.progress_callback("Workflow Complete 🎉", 100)

        if self.stream_response:
            metadata_records = [metadata_exercise_selector, metadata_workout_planner, metadata_warmup]
            return final_workout_plan, metadata_records
        return final_workout_plan
