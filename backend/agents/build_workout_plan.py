from backend.agents.exercise_selector_agent import ExerciseSelectorAgent
from backend.agents.workout_planner_agent import WorkoutPlannerAgent
from backend.agents.personal_trainer_agent import PersonalTrainerAgent


class WorkoutBuilderWorkflow:
    def __init__(self, database_name="workout_builder", progress_callback=None):
        """
        Initializes the Workflow with all agents.
        """
        
        self.exercise_selector = ExerciseSelectorAgent( )
        self.workout_planner = WorkoutPlannerAgent( )
        self.personal_trainer = PersonalTrainerAgent()
        self.progress_callback = progress_callback  # Callback for real-time updates

    
    def run_workflow(self, processed_responses):
        """
        Executes the workflow of building a workout plan.
        """
        print("\n#########User responses: #######\n", processed_responses)

        if self.progress_callback:
            self.progress_callback("Starting Workflow 🚀", 0)

        # Step 1: Exercise Selector
        if self.progress_callback:
            self.progress_callback("Selecting Exercises 🏋️", 20)
        exercises = self.exercise_selector.run(processed_responses)

        # Step 2: Workout Planner
        if self.progress_callback:
            self.progress_callback("Structuring Workout 📋", 50)
        workout_plan = self.workout_planner.run(processed_responses, exercises)

        # Step 3: Personal Trainer
        if self.progress_callback:
            self.progress_callback("Finalizing Workout 🤖", 80)
        final_plan = self.personal_trainer.run(
            processed_responses, workout_plan, exercises)

        if self.progress_callback:
            self.progress_callback("Workflow Complete 🎉", 100)

        return final_plan
