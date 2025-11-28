
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)

import logging
from .llm_service import LLMService
from .prompts import system_prompt, user_prompts_dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
logger = logging.getLogger(__name__)


def summarize_transcript(transcript_text, category):
    """
    Summarizes the transcript dynamically based on the video's category.
    """

    if not transcript_text or transcript_text == "No transcript":
        raise RuntimeError("Transcript is empty.")


    llm = LLMService()
    if category not in user_prompts_dict:

        raise ValueError(f"Unsupported category: {category}.")

    user_prompt_exercises = user_prompts_dict[category]["exercises_prompt"].substitute(
        transcript_text=transcript_text)
    user_prompt_main_knowledge = user_prompts_dict[category]["main_knowledge_prompt"].substitute(
        transcript_text=transcript_text)

    logger.info("Creating summaries for category: %s...", category)

    # Create summaries
    exercises_summary = llm.call_stream_llm(
        system_prompt=system_prompt, user_prompt=user_prompt_exercises)

    logger.info("Exercises summary successfully created!")
    logger.info("Creating Main Knowledge summaries")
    main_knowledge_summary = llm.call_stream_llm(
        system_prompt=system_prompt, user_prompt=user_prompt_main_knowledge)
    logger.info("Main knowledge summary successfully created!")

    return exercises_summary, main_knowledge_summary
