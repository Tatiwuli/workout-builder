from string import Template

system_prompt = """
You are a seasoned personal trainer with expertise in creating efficient, 
science-based workout plans. 
Your goal is to summarize science-backed videos, which is critical to guide another 
personal trainer to create efficient and scientifically sound workout plans tailored to a customer's needs.
A customer's needs encompass: fitness level,time constraint, hypertrophy goals, target muscle group.
Your summary must strictly follow the template given to you.

"""

user_prompts_dict = {
    "workout_session": {
        "exercises_prompt": Template("""Your task is to create a comprehensive, concise, and well-structured summary of the video in the **specified format below**.
                        The summary must preserve all relevant exercise details, scientific insights, and
                        execution instructions while eliminating filler and irrelevant content. These summaries are
                        crucial for personal trainers identifying relevant videos for building workout plans.

                        ### **Instructions for Analysis and Summary Creation**

                            **Warmup**: Explain the warmup exercises in detail , including how to execute each exercise, and the number of sets and reps
                            For each exercise, include the following:
                            - **Setup Notes**: Explain how to setup the equipment and/or position to execute the exercise. Include all the setup tips
                            - **Execution Notes:**  Provide a detailed explanation on how to perform the exercise. DO NOT miss any specific cues, grips positions, form angles, form details.
                            Include any additional execution advices.
                            -**Exercise Warmup**: If mentioned, explain how to conduct the warmup for the exercise, including the number of sets and reps
                            - **Targeted Muscles**: List which muscles the exercise emphasizes.
                            - **Targeted Muscle Part** : List which muscle parts of the muscle group it targets and explain why, connecting anatomical insights when applicable.
                            - **Limitations**: List short descriptions of any constraints or limitations (e.g., "tension only at stretch," "may cause wrist discomfort," "rare equipment").
                            - **Reps and Sets**: Provide the recommended number of sets and reps per set and explain in detail how to executed them. If strategies were mentioned,clearly mention them in the explanation
                            - **Weights**: Explain how to determine the weight for the exercise if the video discusses this.
                            - **Progression**: Include progression advice if provided (e.g., how to increase weight or adjust difficulty over time).
                            - **Alternative Options**: If the video compares the exercise to others, briefly describe the comparison, including the conclusion of it. If alternative ways of performing the same exercise are shown, include a clear explanation of these variations and how they differ from the standard execution.
                        - **Scientific Insights**: If a study is referenced, embed the citation directly into the description. Include the study's name (or how it was referred to in the video) and a detailed explanation of its findings.
                        - **Additional notes**: Include any point about the exercise by Jeff that will be important when building a workout plan of the muscle group

                        ###Notes:

                        - Include ALL the exercises mentioned in the video. Missing exercise is unacepptable
                        - If a section for an exercise is not mentioned in the video, mark it as `"none"`. Do not write anything by your own.
                        - If the video include any example to illustrate a point, include that in the summary.
                        - The video might provide additional advice about an exercise at any random moment. Keep in mind that not all points are presented linearly. Be prepared to revisit
                        and update your summary notes to include these additional insights if they directly relate to earlier points.


                        **Output Format Example in JSON:**

                        ```json

                        {
                            "warmup": {
                                "setup_notes": "",
                                "execution_notes": "",
                                "sets_reps": ""
                            },
                            "exercises": [
                            "exercise_name": {
                                    "setup_notes": "",
                                    "execution_notes": "",
                                    "exercise_warmup": "",
                                    "targeted_muscles": [],
                                    "targeted_muscle_parts": "",
                                    "limitations": "",
                                    "reps_sets": "",
                                    "weights": "",
                                    "progression": "",
                                    "alternative_options": "",
                                    "scientific_insights": "",
                                    "additional_notes": ""
                                },

                                "exercise_name": {
                                    "setup_notes": "",
                                    "execution_notes": "",
                                    "exercise_warmup": "",
                                    "targeted_muscles": [],
                                    "targeted_muscle_parts": "",
                                    "limitations": "",
                                    "reps_sets": "",
                                    "weights": "",
                                    "progression": "",
                                    "alternative_options": "",
                                    "scientific_insights": "",
                                    "additional_notes": ""
                                },
                                ...
                                [Repeat this output structure to all the exercises]
                                ]


                        }


                        Please follow the guidelines above and create a summary for this video. This is the video's transcript:
                        $transcript_text


                            """),

        "main_knowledge_prompt": Template(""" 
                        Your task is to create a comprehensive, concise, and well-structured summary of the video in the ** specified format below**.
                        The summary must preserve all relevant exercise details, scientific insights, and
                        execution instructions while eliminating filler and irrelevant content. These summaries are
                        crucial for personal trainers identifying relevant videos for building workout plans.

                        # Template:

                        1.**Muscle Groups**: List all the muscle groups targetted in the workout video
                        2. ** Muscle Anatomy and Function: ** Highlight targeted muscles parts and their roles as explained in the video.
                        4. ** Form details**: Explain all the form details mentioned when workout out the muscle group. This includes explaining different types of grips and the effect of each one, different angles of a movement, and so on
                        5. ** Strategies**: Explain ** in detail ** any strategies mentioned to perform the sets/reps or to define the weights. Also explain how they're used in the workout.
                        6. **Research Insights**: 
                        - Cite all research mentioned in the video. If specific studies are not explicitly cited, summarize the research as described in the video.
                        - Provide a detailed explanation of the findings and insights from the research, emphasizing how they relate to the discussed exercises and/or muscle group.
                        7. **Optimization/Progression notes**: Explain any advice to progress or optimize the workout of the muscle group
                        **Output Format Example in JSON:**

                        ```json

                        {"muscle_groups": [],

                        "muscle_part_anatomy_function" : [

                            "muscle_part_x": "",
                            ...
                        ],
                        "form_details": "",
                        "strategies": "",
                        "research_insights": "",
                        "optimization_notes": ""

                        }


                        Please follow the guidelines above and create a summary for this video. This is the video's transcript: 
                        $transcript_text
                        """)
    },

    "tier_list": {
        "exercises_prompt":  Template("""
                    Your task is to create a comprehensive, concise, and well-structured summary of the video in the **specified format below**. 
                    The summary must preserve all relevant exercise details, scientific insights, and execution instructions while eliminating filler and irrelevant content. Your summary is crucial for personal trainers selecting relevant exercises that address a customer's needs.

                    ### **Instructions for Analysis and Summary Creation**

                    1. **Exercise Rankings:** 
                        - For each exercise, include the following:
                        - **Setup Notes**: Explain how to setup the equipment and/or position to execute the exercise, if mentioned.
                        - **Execution Notes:** Provide step-by-step guidance on how to perform the exercise, including specific cues, grips positions, form angles, form details. Include any additional execution advice.
                        - **Tier Reason:** List ALL the reasons why the exercise was placed in its tier. Also explain specifically HOW the exercise meets the criteria mentioned previously.
                        - **Targeted Muscles**: List which muscles the exercise emphasizes.
                        - **Targeted Muscle Part**: List which muscle parts of the muscle group it targets and explain why, connecting anatomical insights when applicable.
                        - **Limitations**: List short descriptions of any constraints or limitations (e.g., "tension only at stretch," "may cause wrist discomfort," "rare equipment").
                        - **Alternative Options**: If the video compares the exercise to others, briefly describe the comparison, including the insights from it. If alternative ways of performing the same exercise are shown, include a clear explanation of these variations, including detailed execution instructions (if different from the standard execution) and how they differ from the standard execution.
                        - **Scientific Insights**: If a study is referenced, embed the citation directly into the description. Include the study's name (or how it was referred to in the video) and a detailed explanation of its findings.
                        - **Additional Notes**: Include any point about the exercise related to execution, setup, time constraints, or Jeff's personal opinion.

                    ### Notes:  
                    - EVERY EXERCISE THAT HAS A TIER ASSIGNED TO IT , regardless of which tier, should be included to the summary as one exercise.  Missing exercises is unacceptable.
                    - If an additional Tier name is introduced, include the Tier section in the summary with all its exercises.
                    - If a section for an exercise is not mentioned in the video, mark it as `"none"`. Do not write anything by your own.
                    - Write as specific as you can! NEVER use general phrases that don't explain much about the point.
                    - The video might provide additional advice about an exercise at any random moment. Keep in mind that not all points are presented linearly. Be prepared to revisit and update your summary notes to include these additional insights if they directly relate to earlier points.

                    **Output Format Example in JSON:**

                    ```json
                    {
                    "exercise_rankings": {
                        "S-Tier": [
                        {
                            "exercise_name": "",
                            "setup_notes": "",
                            "execution_notes": "",
                            "tier_reasons": "",
                            "targeted_muscles": [],
                            "targeted_muscle_parts": "",
                            "limitations": "",
                            "alternative_options": "",
                            "scientific_insights": "",
                            "additional_notes": ""
                        },
                        {
                            "exercise_name": "",
                            "setup_notes": "",
                            "execution_notes": "",
                            "tier_reasons": "",
                            "targeted_muscles": [],
                            "targeted_muscle_parts": "",
                            "limitations": "",
                            "alternative_options": "",
                            "scientific_insights": "",
                            "additional_notes": ""
                        }
                        ]
                    }
                    }
                    ```

                    Please follow the guidelines above and create a summary for this video. This is the video's transcript: 
                    $transcript_text
                    """),

        "main_knowledge_prompt": Template("""
                    Your task is to create a comprehensive, concise, and well-structured summary of the video in the **specified format below**. 
                    The summary must preserve all relevant insights about research findings, the specified muscle groups' training, anatomy, functions, and additional advice while eliminating filler and irrelevant content. Your summary is crucial for personal trainers developing a solid understanding of training the specified muscle group. 

                    ### Template: 

                    1. **Muscle Group**: List all the muscle groups targeted in the video's exercises.
                    2. **Ranking Criteria**: 
                        - "[Criterion 1]": "[Briefly explain what does Jeff Nippard mean by that]",
                        - "[Criterion 2]": "[Briefly explain what does Jeff Nippard mean by that]",
                        - "[Criterion 3]": "[Briefly explain what does Jeff Nippard mean by that]"
                        - Include any more criteria if mentioned.

                    3. **Muscle Anatomy and Function:** Highlight targeted muscles parts and their roles as explained in the video.
                    4. **Form Details**: Explain all the form details mentioned when working out the muscle group. This includes explaining different types of grips and the effect of each one, different angles of a movement, and so on.
                    5. **Training Keys**: Explain in detail how one should train the specified muscle part, including any advice mentioned. Connect the insights with the muscles' anatomy and function.
                    6. **Research Insights**: 
                        - Cite all research mentioned in the video. If specific studies are not explicitly cited, summarize the research as described in the video.
                        - Provide a detailed explanation of the findings and insights from the research, emphasizing how they relate to the discussed exercises and/or muscle group.

                    7. **Optimization/Progression Notes**: Explain any advice to progress or optimize the workout of the muscle group.

                    **Output Format Example in JSON:**

                    ```json
                    {
                    "muscle_group": [],
                    "criterias": [
                        {
                        "criteria_x": ""
                        }
                    ],
                    "muscle_part_anatomy_function": [
                        {
                        "muscle_part_x": ""
                        }
                    ],
                    "form_details": "",
                    "training_keys": "",
                    "research_insights": "",
                    "optimization_notes": ""
                    }
                    ```

                    Please follow the guidelines above and create a summary for this video. This is the video's transcript: 
                    $transcript_text
                    """)
    }
}
