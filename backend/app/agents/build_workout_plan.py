from .exercise_selector_agent import ExerciseSelectorAgent
from .workout_planner_agent import WorkoutPlannerAgent
from .personal_trainer_agent import PersonalTrainerAgent
from ..database.mongodb_handler import WorkoutBuilderDatabaseHandler

from ..services.workout_knowledge_fetch import WorkoutKnowledgeFetch


class WorkoutBuilderWorkflow:
    def __init__(self, database_name="workout_builder", progress_callback=None):
    
        self.knowledge_fetch = WorkoutKnowledgeFetch()
        self.progress_callback = progress_callback
        

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

    def run_workflow(self, processed_responses):
        if self.progress_callback:
            self.progress_callback("Starting Workflow 🚀", 0)

        if self.progress_callback:
            self.progress_callback("Fetching common data...", 10)
        workout_knowledge = self.fetch_workout_knowledge(processed_responses)

        if self.progress_callback:
            self.progress_callback("Selecting Exercises 🏋️", 20)
        exercise_selector = ExerciseSelectorAgent(
            processed_responses,
            workout_knowledge=workout_knowledge,
            stream_response = True ,
        )
        exercise_selector_output = exercise_selector.run()

        if self.progress_callback:
            self.progress_callback("Structuring Workout 📋", 50)
        workout_planner = WorkoutPlannerAgent(
            processed_responses,
            exercise_selector_output,
            workout_knowledge=workout_knowledge,
            stream_response = True ,
        )
        workout_plan = workout_planner.run()

        if self.progress_callback:
            self.progress_callback("Finalizing Workout 🤖", 80)
        personal_trainer = PersonalTrainerAgent(
            workout_knowledge=workout_knowledge,
            stream_response = True ,
        )
        final_plan = personal_trainer.run(
            processed_responses,
            workout_plan,
            exercise_selector_output
        )

        if self.progress_callback:
            self.progress_callback("Workflow Complete 🎉", 100)

        return final_plan
