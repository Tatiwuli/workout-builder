from typing import Optional


DIRECT_GOAL_KEYS = {
    "back",
    "chest",
    "shoulders",
    "triceps",
    "glutes",
    "hamstrings",
    "quadriceps",
    "calves",
}


def _normalise_muscle_slug(raw_key: str) -> Optional[str]:
    cleaned_key = (raw_key or "").strip()
    if not cleaned_key:
        return None
    return cleaned_key.lower().replace(" ", "_")


def process_user_responses(user_responses):
    """
    Processes raw user responses to pass to agents
    
    Args:
        user_responses (dict): Raw user input from questionnaire
        
    Returns:
        dict: Processed responses with computed fields
    """
    workout_duration = user_responses.get("workout_duration", 0)

    if workout_duration < 45:
        time_constraint = "short"
    elif 45 <= workout_duration <= 60:
        time_constraint = "medium"
    else:
        time_constraint = "long"

  
    fitness_level_mapping = {
        "I'm just starting out and have less than 3 months of experience.": "beginners",
        "I've been consistently training for 3 months to 1 year.": "beginners",
        "I've been training regularly for 1 to 2 years": "intermediate_early",
        "I've been training regularly for 2 to 3 years": "intermediate_late",
    }
    fitness_level = fitness_level_mapping.get(
        user_responses.get("experience_level_description"), "beginners"
    )

    muscle_goals = {}
    for muscle_key, goal in user_responses.items():
        if not goal:
            continue

        if muscle_key.endswith("_goal"):
            slug = _normalise_muscle_slug(muscle_key[:-5])
            if not slug:
                continue
            muscle_goals[f"{slug}_goal"] = goal
            continue

        slug = _normalise_muscle_slug(muscle_key)
        if slug in DIRECT_GOAL_KEYS:
            muscle_goals[f"{slug}_goal"] = goal

    muscle_workout_frequency = {
        muscle: frequency
        for muscle, frequency in user_responses.items()
        if muscle.endswith("_frequency") and frequency
    }

    final_user_responses = {
        "muscle_groups": user_responses.get("muscle_groups"),
        "goals": muscle_goals,
        "muscle_workout_frequency": muscle_workout_frequency,
        "workout_duration": workout_duration,
        "time_constraint": time_constraint, 
        "fitness_level": fitness_level, 
        "experience_level_description": user_responses.get("experience_level_description"),  
    }

    return final_user_responses


