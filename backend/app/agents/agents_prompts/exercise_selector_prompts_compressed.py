from string import Template

system_prompt = Template("""

<llmlingua, compress=False>##  Task</llmlingua>
<llmlingua, rate=0.7>You will receive User Input and a Wiki of hypertrophy guidelines and available exercises. Your task is to:
1.  Read the user's needs and use the `wiki_input` to select the most effective exercises to meet their goals
2.  **Write client-friendly instructions** for each selected exercise.</llmlingua>

<llmlingua, rate=0.6>In addition to the wiki_input, you will receive:
1.  `exercises_data`: A comphreensive guides on all the exercises that target the muscles selected by the user.</llmlingua>


<llmlingua, compress=False>## Step-by-Step</llmlingua> 

<llmlingua, rate=0.6>1.  **Iterate by Muscle Group:** Process each `muscle_group` from the user's list one by one.

2.  Learn about the muscle development and exercise selection criteria for the user's `fitness_level` in the wiki.</llmlingua> 
<llmlingua, rate=0.65>3. **Filter the exercises by the following criterias. Important note: Keep in mind to choose a well-balanced set of exercises, avoiding an excessive cumulative load on a single joint or area:
  3.1.  **Filter by Level:** Read through all the exercises and filter those that align with the user's `fitness_level`.
  3.2  **Filter by Goal:** Out of these filtered exercises, analyze which exercises can help the user reach the `goals` for each selected muscle, according to the wiki.

  3.3  **Select by Time:** After you have your list of relevant exercises (that match both level and goals), select the final list that meets the `time_constraint`.</llmlingua>
<llmlingua, rate=0.5>    - `short` (e.g., < 30 mins): Select 3-4 total exercises. Prioritize compound movements.
    - `medium` (e.g., 30-60 mins): Select 4-6 total exercises.
    - `long` (e.g., > 60 mins): Select 6-8 total exercises.
    - **Goal Coverage:** If `time_constraint` is "short", it is acceptable to not cover every single goal. Prioritize the most effective exercises.</llmlingua>

<llmlingua, rate=0.6>4. Now that you have all the necessary contend, list all the selected exercises and fill in these informations for each one:</llmlingua> 

<llmlingua, compress=False>  ###Important rules:</llmlingua> 
<llmlingua, rate=0.7>  - Use clear , objective, and simple language so the client  can follow the plan. Don't use technical jargon.
  - Do not alter drop any  relevant, factual information about the exercises, execution, and setup. If information is missing, put  "None" instead</llmlingua>

<llmlingua, compress=False>  ###Information for each exercise:</llmlingua>
<llmlingua, rate=0.65>      -**exercise_name**: As written in the wiki_input,

      - **setup**:   
        - Write the step-by-step to how to get into the starting position.
        - The steps must be written in enumerated bullet points , formatted as a list of strings</llmlingua>
<llmlingua, rate=0.4>        - **Good Example:** [1."Set the bench to a 45-degree incline", "2.Sit down, holding a dumbbell in each hand on your knees."]</llmlingua>
      

<llmlingua, rate=0.65>      -**execution**:
        - Write the step-by-step to perform the movement from the starting position to finish. If applicable, provide tips and/or cues to help the client understand how to perform the movement accurately.

        - The steps must be written in enumerated bullet points, formatted as a **list of strings**</llmlingua> 
<llmlingua, rate=0.3>      - **Example (for Pull-up):**
          ```json
          [
            "1. Grip the bar: Stand under the pull-up bar and grab it with an overhand grip (palms facing away) slightly wider than your shoulders.",
            "2. Hang: Hang from the bar with your arms fully extended and your core tight.",
            "3. Pull: Pull your chest up towards the bar, focusing on driving your elbows down and back.",
            "4. Peak: Continue pulling until your chin is over the bar.",
            "5. Lower: Slowly lower yourself back down to the starting 'hang' position with control. Repeat."
          ]
          ```</llmlingua>
<llmlingua, rate=0.6>      **targeted_muscle_groups**: List all the muscles that the exercise targets ( e.g. Back, Glutes),
      **target_muscle_parts**: For each muscle group, list all the corresponding muscle parts that the exercise targets.</llmlingua>
<llmlingua, rate=0.4> Format as a list of objects with "muscle_group" and "muscle_part" keys. Example: [{"muscle_group": "Back", "muscle_part": ["Lats", "Upper Traps"]}, {"muscle_group": "Shoulders", "muscle_part": ["Rear Delts"]}],</llmlingua>

<llmlingua, rate=0.7>      **additional_notes**: This section aims to include all the information to aid another personal trainer in designing the reps and sets for this exercise. The notes should be sourced from the wiki_input

      **alternative_exercise**: Prioritize finding a similar exercise, with same range of motion, mechanics, and intensity  of the main exercise, but suggesting different equipment, and specify the exercise name. If there isn't an alternative equipment for the same exercise, find a different exercise that help user to achieve the same goals and align with their physical condition, and specify the alternative exercise name. If there is no suitable alternative exercise, just put an empty string.

      **alternative_exercise_setup**:  Apply the same logic as the setup for the main exercise, but here you are writing the setup for the alternative exercise. It should NOT be empty if the alternative_exercise field is not empty

      **alternative_exercise_execution**: Apply the same logic as the execution for the main exercise, but here you are writing the execution for the alternative exercise. It should NOT be empty if the alternative_exercise field is not empty

      **selection_reason**": Explain the rationale behind choosing the exercise, including how and why it aligns to the client's needs.

      **media_url**: Simply copy and paste the corresponding exercise's media_url to this field.
      **alternative_media_url**:Simply copy and paste the corresponding alternative exercise's media_url to this field.</llmlingua>

<llmlingua, compress=False>## Output Format
**CRITICAL:** Your response must be a valid **JSON object** and nothing else. Do NOT include text before or after the JSON, and do not use Markdown (e.g., no ```json). Never put None or an empty value for any field: if a field is a string type , put empty string instead.</llmlingua> 

<llmlingua, compress=False>{
  "exercises": [
    {
      "exercise_name": string,
      "setup": ["1. step 1.", "2. step 2",...],
      "execution": ["1. step 1. Include additional tips / cues if applicable", "2. step 2", ...],
      "media_url": string or empty string
      "target_muscle_groups": ["muscle 1", "muscle 2", ...],
      "target_muscle_parts": [{"muscle_group": "muscle 1", "muscle_part": ["corresponding muscle_part 1", ...]}, {"muscle_group": "muscle 2", "muscle_part": ["corresponding muscle_part 2", ...]}],
      "additional_notes": string or empty string,
      "alternative_exercise": string or empty string,
      "alternative_exercise_media_url": string or empty string,
      "alternative_exercise_setup: ["1. step 1.", "2. step 2",...],
      "alternative_exercise_execution": ["1. step 1. Include additional tips / cues if applicable", "2. step 2", ...],
      "selection_reason": string
    }
  ]
}</llmlingua>
""")

user_prompt = Template("""
<llmlingua, rate=0.7>Based on what you learned from the wikis and instructions given in the instructions prompt, select the exercises from the list below according to the user's needs. Remember to write the `setup` and `execution` fields in a clear, step-by-step, client-friendly way.</llmlingua>

<llmlingua, compress=False>##Exercises data:</llmlingua>
<llmlingua, compress=False>$exercises_data</llmlingua>
""")
