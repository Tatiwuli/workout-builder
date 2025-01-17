from agents.exercise_selector_agent import ExerciseSelectorAgent
from agents.workout_planner_agent import WorkoutPlannerAgent
from agents.personal_trainer_agent import PersonalTrainerAgent


class WorkoutBuilderWorkflow:
    def __init__(self, database_name="workout_builder", progress_callback=None, api_key = None, secrets_mongo_uri = None):
        """
        Initializes the Workflow with all agents.
        """
        if not api_key:
            raise ValueError("API key is required to initialize the workflow.")

        self.exercise_selector = ExerciseSelectorAgent(api_key= api_key, secrets_mongo_uri = secrets_mongo_uri)
        self.workout_planner = WorkoutPlannerAgent(api_key= api_key, secrets_mongo_uri = secrets_mongo_uri)
        self.personal_trainer = PersonalTrainerAgent(api_key= api_key, secrets_mongo_uri = secrets_mongo_uri)
        self.progress_callback = progress_callback  # Callback for real-time updates

    
    def run_workflow(self, user_needs):
        """
        Executes the workflow of building a workout plan.
        """
        if self.progress_callback:
            self.progress_callback("Starting Workflow 🚀", 0)

        # Step 1: Exercise Selector
        if self.progress_callback:
            self.progress_callback("Selecting Exercises 🏋️", 20)
        exercises = self.exercise_selector.run(user_needs)

        # Step 2: Workout Planner
        if self.progress_callback:
            self.progress_callback("Structuring Workout 📋", 50)
        workout_plan = self.workout_planner.run(user_needs, exercises)

        # Step 3: Personal Trainer
        if self.progress_callback:
            self.progress_callback("Finalizing Workout 🤖", 80)
        final_plan = self.personal_trainer.run(
            user_needs, workout_plan, exercises)

        if self.progress_callback:
            self.progress_callback("Workflow Complete 🎉", 100)

        return final_plan
