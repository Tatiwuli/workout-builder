from exercise_selector_agent import ExerciseSelectorAgent
from workout_planner_agent import WorkoutPlannerAgent
from personal_trainer_agent import PersonalTrainerAgent


class WorkoutBuilderWorkflow:
    def __init__(self, database_name="workout_builder"):
        """
        Initializes the Workflow with all agents.
        """
        self.exercise_selector = ExerciseSelectorAgent()
        self.workout_planner = WorkoutPlannerAgent()
        self.personal_trainer = PersonalTrainerAgent()

    def run_workflow(self, user_needs):
        """
        Executes the complete workflow of building a workout plan.

        Args:
            user_needs (dict): User-specific requirements.

        Returns:
            dict: Final workout plan.
        """
        print("=== Starting Workout Builder Workflow ===")

  
        print("\n--- Exercise Selector is selecting the exercises ---")
        exercise_selector_output = self.exercise_selector.run(user_needs)
        print("Selected Exercises Output:", exercise_selector_output)

     
        print("\n--- Workout Planner is structuring the workout ---")
        planned_workout = self.workout_planner.run(
            user_needs, exercise_selector_output
        )
        print("Planned Workout Output:", planned_workout)

       
        print("\n--- Personal Trainer is finalizing the workout plan ---")
        final_workout_plan = self.personal_trainer.run(
            user_needs, workout_plan_draft=planned_workout, selected_exercises=exercise_selector_output
        )
        print("Final Workout Plan Output:", final_workout_plan)

        print("\n=== Workflow Completed Successfully ===")
        return final_workout_plan


# Example Usage
if __name__ == "__main__":
    # Define user needs
    user_needs = {
        "muscle_groups": ["Glutes", "Quadriceps", "Hamstrings"],
        "workout_duration": 60,  # Total workout time including warmup
        "time_range": "mid",
        "weekly_workout_frequency(n sessions)": {"Glutes": 2, "Quadriceps": 2, "Hamstrings": 2},
        "goals": ["Rounded glutes", "Glutes focus", "Defined Quadriceps"],
        "fitness_level": "intermediate_early"
    }

    # Initialize the workflow
    workflow = WorkoutBuilderWorkflow()

    # Run the workflow
    final_workout_plan = workflow.run_workflow(user_needs)

    # Print the final output
    print("\nFinal Output:", final_workout_plan)
