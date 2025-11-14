from .exercise_selector_agent import ExerciseSelectorAgent
from .workout_planner_agent import WorkoutPlannerAgent
from .personal_trainer_agent import PersonalTrainerAgent
from ..database.mongodb_handler import WorkoutBuilderDatabaseHandler

from ..services.workout_knowledge_fetch import WorkoutKnowledgeFetch

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

    def run_workflow(self, processed_responses: Dict[str, Any]) -> Union[Dict[str, Any], Tuple[Dict[str, Any], List[Dict[str, Any]]]]:
        if self.progress_callback:
            self.progress_callback("Starting Workflow 🚀", 0)

        if self.progress_callback:
            self.progress_callback("Fetching common data...", 10)

        workout_knowledge = self.fetch_workout_knowledge(processed_responses)

        metadata_records: List[Dict[str, Any]] = []

        if self.progress_callback:
            self.progress_callback("Selecting Exercises 🏋️", 20)

        exercise_selector = ExerciseSelectorAgent(
                processed_responses,
                workout_knowledge=workout_knowledge,
                stream_response=self.stream_response,
            )
        if self.stream_response:
            exercise_selector_output,metadata_exercise_selector = exercise_selector.run()
        else: 
            exercise_selector_output = exercise_selector.run()


        if self.progress_callback:
            self.progress_callback("Structuring Workout 📋", 50)
        workout_planner = WorkoutPlannerAgent(
            processed_responses,
            exercise_selector_output,
            workout_knowledge=workout_knowledge,
            stream_response=self.stream_response,
        )
        if self.stream_response:
            workout_planner_output,metadata_workout_planner = workout_planner.run()
        
        else: 
            workout_planner_output  = workout_planner.run()

        if self.progress_callback:
            self.progress_callback("Finalizing Workout 🤖", 80)
        personal_trainer = PersonalTrainerAgent(
            workout_knowledge=workout_knowledge,
            stream_response=self.stream_response,
        )

        if self.stream_response:
            personal_trainer_output, metadata_personal_trainer = personal_trainer.run(processed_responses,
            workout_planner_output,
            exercise_selector_output)
        else:
            personal_trainer_output = personal_trainer.run(
                processed_responses,
                workout_planner_output,
                exercise_selector_output
            )

        if self.progress_callback:
            self.progress_callback("Workflow Complete 🎉", 100)

        if self.stream_response:
            metadata_records =  [metadata_exercise_selector, metadata_workout_planner, metadata_personal_trainer]
            return personal_trainer_output, metadata_records
        return personal_trainer_output
