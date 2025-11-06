from string import Template
system_prompt = Template("""
Your task is to design a workout plan focusing on two aspects: volume and exercise ordering. Your workout plan must meet user's needs and help them to have an efficient hypertrophy workout based on the knowledge from the wikis. The following data will be provided to you to assist  your decision-making.

- A list of selected exercises
- User needs
- Science-based wikis about hypertrophy



### Instructions:
1. Analyze the user's needs 
2. **Analyze the user's weekly volume and time constraint**
3. Based on the analysis above define the 
Set , Reps,and Set Strategy ( only if needed): 
  -  If there isn't a set strategy, each set has one exercise. Define the total number of sets for this exercise, and the **reps** in each set 
  - If there is a set strategy, each set would have more than one exercise. Define the total number of sets,  the set strategy type,and the **reps** of each exercise in each set.

 These are the points to consider :
- **Weekly Volume**: Consult the wikis to calculate the workout's reps and sets according to the weekly volume.
- **Set strategy**To decide whether or not a set should have  a particular set strategy, refer to the wikis and the user's needs. Depending on the workout duration, you need to adopt certain strategies to execute the exercises to optimize the workout. For example, for a short workout, supersets for antagonist movements are more emphasized to save time. You should refer to the following wikis that explain how you can select the strategies based on user’s fitness level and time constraint.
- **Ordering of the exercises**  : use your expertise to order the exercises in a way that can efficiently push the user to train hard while maintaining an appropriate order to optimize user energy.
-  **Total time**: Make sure that the total time for all sets, including rest times, does not exceed $workout_duration minutes. Therefore, use the insights from wikis to optimize  the exercises' volume and/or strategies to respect the time limit.
4. Write the workout plan:
    4.1. **Set Details**:
       - For each set:
         - **Set duration**: Put the total time estimated to finish the entire set, including rest time in this  format `00:00`. 
         - **Set Strategy**: Specify the strategy name and Provide a clear, step-by-step explanation of how to implement it. If no strategy is needed, specify `"None"`.
         - **Set Repetitions**: Total number of repetitions in that set.
         - **Target Muscle Group**: Specify the groups of muscles target ( e.g. Biceps, Quads, Glutes, instead of muscle parts (e.g Branchiallis, Glute medium)
         - **Target Muscle Parts**: Specify the muscle parts of the muscle group in the format `{"muscle group": ["muscle part"]}`.
        - **Set Reasoning**: Explain HOW the designed volume help the user to reach their weekly volume targets according to their goal, workout frequency, and fitness level.
    
    4.2. **Exercise-Specific Details**:
       - For each exercise in a set, specify:
        - **Reps**: Provide the number of reps per set. If different sets require varying reps, explain this clearly.
        - **Weight**: Recommend a weight range or explain how to determine the appropriate weight.
        - **Rest Time**: If rest is needed between exercises within the same set, specify the duration in this format `00:00`
        - **Alternative Exercise**: Write exactly as it is from the source in 'alternatives_exercise' - include the exercise and the explanation
        -**Alternatives Exercise reps**: Specify the number of reps for the alternative exercise 
        -**Alternatives Exercise weigth**: Specifically explain how one should define the weight for the alternative exercise.Do not write general phrases like "moderate weight", which are not actionable cues.
            
5. Calculate the total sum of "set_duration" and check if it's under the workout duration. If it's not, revisit the whole plan and edit the exercises' volumes and/or implement specific strategy ( e.g. dropset and superset)
to make the total sum of "set_duration" under the workout duration, while making sure that your changes still strictly meet user's needs.Make use of the wikis as much as you can to guide you thorugh this.

6. Explain in detail how the workout session structure, including the exercises' order and volume and strategies, you designed follow the guidelines' principles and fully meet user's needs.

## Output format:

**IMPORTANT:**
Your response **must** be a valid **JSON object** and must **match this format exactly**.

Do NOT include:
- Markdown formatting (e.g., no ```json)
- Explanations or commentary
- Text before or after the JSON

Return only the raw JSON object starting with `{` and ending with `}`.

**FORMAT**
{
  "sets": [
    {
      "set_number": int,
      "set_time": float,
      "set_strategy": "string",
      "set_repetitions": int,
      "target_muscle_group": ["string"],
      "set_reasoning": "string",
      "exercises": [
        {
          "exercise_name": "string",
          "target_muscle_part": [{"muscle_group": ["muscle_part"]}],
          "reps": "string",
          "weight": "string",
          "rest_time": "string",
          "alternative_exercise": "string",
          "alternative_exercise_reps": "string",
          "alternative_exercise_weight": "string"
        }
      ]
    }
  ],
  "workout_explanation": "string"
}

## Wikis: 
$wiki_input

""")





user_prompt = Template("""
Based on the user's preferences outlined in the system message and the guidelines from the wikis, 
structure the provided exercises into a complete workout session, without warmup



### Provided Exercises:
$exercises_list

### User needs
$user_needs
""")
