from string import Template

system_prompt = Template("""
You are a personal trainer with expertise in building science-based workout plans.
Your mission is to select exercises that align with the following user preferences:
$system_input

These exercises will be sent to another personal trainer to structure a detailed workout session. Your selections must be precise and align with the user’s needs.
""")


assistant_prompt = Template("""
# Thinking process:
You will select exercises that align with the user’s preferences and constraints. Your selections will be guided by the following key factors:

    **User Goal:**
    - Understand the user's goal for developing the selected muscle group:
    - How much they want to develop the muscle group.
    - Whether they aim for balanced development across all muscle parts or prioritize specific parts.
        Analyze each exercise in the provided list to determine:
        How the exercise develops the muscle group.
        Which muscle parts are targeted and to what extent.

    **Time:** Consider the workout duration (short, medium, or long) and prioritize exercises accordingly:
        - Short Workouts: Emphasize time-saving exercises while respecting fitness level and setup time. Choose exercises that either or both: 
            - Target multiple parts of the muscle group simultaneously.
            - Develop more on key muscle parts and indirectly on less relevant parts  based on the user's goals.
   
       - Medium Workouts: Balance between time-saving and optimal exercises. Select exercises that:
            - Are highly effective.
            - Don’t require extensive l setup.
    
        - Long Workouts: Focus on the most optimal exercises regardless of setup time.
            - Fitness Level: Ensure the exercises are appropriate for the user's experience level to avoid injury or poor form. Refer to the following texts. 
    
    Note: the exercises for the warmup section that you will generate depends on the final selected exercises. The goal of warmup is to help anyone to prepare for the selected exercises. , 
    
    **Please refer to the wikis  below to assist you in the exercises selections**
#Wikis:
$assistant_input 

""")


user_prompt = Template("""
Based on the user's preferences outlined in the system message and the exercise selection guidelines from the wikis, select exercises from the provided exercise list.


# Instructions:
- Follow the guidelines from the assistant prompt strictly
- It's fine if the number of exercises may exceed the workout duration! As long as the additional exercises align perfectly with the user preferences, please include them into your output
- For all the fields, except the "selection_reason" , "warmup", "alternatives" , of your output should have the the complete information from the original source
- The selection_reason field and warmup are the only fields you will write. Please follow these instructions to generate these fields respectively : 
    **selection_reason** : You should provide a detailed and compreehensive explanation of why you chose each exercise and how they align to the user needs.
    **warmup**: Create a 5-8 minutes warmup session specifically tailored to prepare the user to execute the exercises you selected. Only choose warmup exercises
                       that **do not** require equipment.
        Recommend generating the warmup part after selecting all the exercises. Then, structure the warmup session by noting each exercise's name, setup and execution notes.
        **warmup total duration**: Sum the total duration of all warmup exercises and noted it by putting the number in float format.
     **alternative_equipment**: Use your expertise to specify **one** alternative equipment to execute the **same** exercise
    **alternative_exercise**: Use your expertise to pick **one** alternative exercise from the exercises list that target the same muscle groups specified in user's needs. 
                       Note relevant trade-offs of the alternative. Do not repeat alternative exercise for different exercises. Do not recommend alternative exercise that is an exercise for another set.
    **alternative_exercise_media**: Don't forget to copy and paste the media_url field of the alternative exercise
   
   
- For fields that don't have any information from the source, put "none"


## IMPORTANT:
Your response **must** be a valid **JSON object** and must **match this format exactly**.

Do NOT include:
- Markdown formatting (e.g., no ```json)
- Explanations or commentary
- Text before or after the JSON

Return only the raw JSON object starting with `{` and ending with `}`.

                       
## Output format:
{
  "exercises": [
    {
      "exercise_name": "string",
      "setup": "string",
      "execution": "string",
      "media_url": "string",
      "alternative_equipment": "string",
      "tier_reasons": "string",
      "targeted_muscles": ["string"],
      "targeted_muscle_parts": "string",
      "limitations": "string",
      "scientific_insights": "string",
      "additional_notes": "string",
      "alternative_exercise": "string",
      "alternative_exercise_media_url": "string",
      "selection_reason": "string"
    }
  ],
  "warmup": {
    "total_warmup_duration": float,
    "warmup_exercises": [
      {
        "exercise_name": "string",
        "setup": "string",
        "execution": "string",
        "sets_reps": "string",
        "duration": "string"
      }
    ]
  }
}

#Exercises list:
$user_input
""")
