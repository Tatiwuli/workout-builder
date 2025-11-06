import argparse
import json
import logging
import os
from typing import Any, Dict

from ..app.agents.build_workout_plan import WorkoutBuilderWorkflow
from ..app.services.user_response_processor import process_user_responses


logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


def run_from_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the full workout generation workflow.

    Args:
        user_data: Raw data matching API schema (muscle_groups, goal, frequency, duration, experience, ...)

    Returns:
        Final workout plan as dict
    """
    # Prepare raw responses for processing
    raw_responses = {
        "muscle_groups": user_data["muscle_groups"],
        "goal": user_data.get("goal", ""),
        "frequency": user_data.get("frequency", ""),
        "workout_duration": user_data["duration"],
        "experience_level_description": user_data["experience"],
        **(user_data.get("muscle_goals") or {}),
        **(user_data.get("muscle_frequencies") or {}),
    }

    # Process user responses (maps to MongoDB-compatible fields)
    processed_responses = process_user_responses(raw_responses)

    # Run workflow with processed responses
    workflow = WorkoutBuilderWorkflow()
    return workflow.run_workflow(processed_responses)


def _parse_args():
    parser = argparse.ArgumentParser(description="Run workout plan workflow")
    parser.add_argument("--input-json", type=str, help="Path to JSON file with user data", required=False)
    return parser.parse_args()


def main():
    args = _parse_args()
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY must be set in environment")
    if not os.getenv("MONGODB_URI"):
        raise RuntimeError("MONGODB_URI must be set in environment")

    user_data = {
            "muscle_groups": ["Chest"],
            "goal": "Bigger chest",
            "frequency": 4,
            "duration": 60,
            "experience": "I've been consistently training for 3 months to 1 year.",
            "muscle_goals": {"Chest": "Bigger chest"},
            "muscle_frequencies": {"Chest": 4},
        }

    logger.info("Running workflow...")
    logger.info("Step 1: Processing user responses...")
    logger.info("Step 2: Exercise Selector Agent (new implementation)...")
    logger.info("Step 3: Workout Planner Agent...")
    logger.info("Step 4: Personal Trainer Agent...")
    
    final_plan = run_from_user_data(user_data)
    
    logger.info("Workflow completed successfully!")
    print(json.dumps(final_plan, indent=2))


if __name__ == "__main__":
    main()


