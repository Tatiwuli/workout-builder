
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)

from llms.llm import OpenAILLM
from data_preparation.prompts import system_prompt, user_prompts_dict


# init LLM model
llm = OpenAILLM(model_name = "gpt-4o")


def summarize_transcript(transcript_text, category):
    """
    Summarizes the transcript dynamically based on the video's category.
    """
   
    if category not in user_prompts_dict:

        raise ValueError(f"Unsupported category: {category}.")

    user_prompt_exercises = user_prompts_dict[category]["exercises_prompt"].substitute(transcript_text=transcript_text)
    user_prompt_main_knowledge = user_prompts_dict[category]["main_knowledge_prompt"].substitute(transcript_text=transcript_text)


    print(f"Creating summaries for category: {category}...")

    # Create summaries
    exercises_summary = llm.call_api( system_prompt=system_prompt,user_prompt=user_prompt_exercises),
    
    print("Exercises summary successfully created!")

    main_knowledge_summary = llm.call_api(system_prompt=system_prompt,user_prompt=user_prompt_main_knowledge)
    print("Main knowledge summary successfully created!")

    return exercises_summary, main_knowledge_summary
