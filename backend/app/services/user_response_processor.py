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
        user_responses["time_range"] = "short"
    elif 45 <= workout_duration <= 60:
        user_responses["time_range"] = "mid"
    else:
        user_responses["time_range"] = "long"

    experience_mapping = {
        "I'm just starting out and have less than 3 months of experience.": "Early Beginner",
        "I've been consistently training for 3 months to 1 year.": "Beginner",
        "I've been training regularly for 1 to 2 years": "Early Intermediate",
        "I've been training regularly for 2 to 3 years": "Late Intermediate",
    }
    user_responses["experience_level"] = experience_mapping.get(
        user_responses.get("experience_level_description"), "Unknown"
    )

    muscle_goals = {
        muscle: goal
        for muscle, goal in user_responses.items()
        if muscle.endswith("_goal") and goal
    }

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
        "time_range": user_responses.get("time_range"),
        "experience_level": user_responses.get("experience_level"),
        "experience_level_description": user_responses.get("experience_level_description"),
    }

    return final_user_responses


