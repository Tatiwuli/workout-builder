import argparse
import json
import logging
import os
from typing import Any, Dict

from ..llms.gemini_connector import GeminiWorkflow


logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


def run_from_user_data(user_data: Dict[str, Any], *, model: str = "gemini-2.5-flash", temperature: float = 0.0) -> Dict[str, Any]:
    """
    Run the full workout generation workflow with Gemini.

    Args:
        user_data: Raw data matching API schema (muscle_groups, goal, frequency, duration, experience, ...)
        model: Gemini model id, defaults to gemini-2.5-flash
        temperature: Sampling temperature

    Returns:
        Final workout plan as dict
    """
    workflow = GeminiWorkflow(model=model, temperature=temperature)
    return workflow.run_full_workflow(user_data)


def _parse_args():
    parser = argparse.ArgumentParser(description="Run workout plan workflow using Gemini")
    parser.add_argument("--input-json", type=str, help="Path to JSON file with user data", required=False)
    parser.add_argument("--model", type=str, default="gemini-2.5-flash", help="Gemini model id")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature")
    return parser.parse_args()


def main():
    args = _parse_args()
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY must be set in environment")
    if not os.getenv("MONGODB_URI"):
        raise RuntimeError("MONGODB_URI must be set in environment")

    if args.input_json and os.path.exists(args.input_json):
        with open(args.input_json, "r", encoding="utf-8") as f:
            user_data = json.load(f)
    else:
        # Minimal interactive fallback (useful for quick manual runs)
        logger.info("No --input-json provided; using interactive prompts")
        muscle_groups = input("Comma-separated muscle groups (e.g., Chest,Biceps): ").strip().split(",")
        goal = input("Goal (e.g., Hypertrophy): ").strip()
        frequency = input("Weekly frequency (e.g., 3): ").strip()
        duration = int(input("Workout duration in minutes (e.g., 60): ").strip())
        experience = input("Experience description: ").strip()
        user_data = {
            "muscle_groups": [m.strip() for m in muscle_groups if m.strip()],
            "goal": goal,
            "frequency": frequency,
            "duration": duration,
            "experience": experience,
            "muscle_goals": {},
            "muscle_frequencies": {},
        }

    logger.info("Running workflow...")
    final_plan = run_from_user_data(user_data, model=args.model, temperature=args.temperature)
    print(json.dumps(final_plan, indent=2))


if __name__ == "__main__":
    main()


