
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
logger = logging.getLogger(__name__)

"""

fetched_transcript = ytt_api.fetch(video_id)

# is iterable
for snippet in fetched_transcript:
    print(snippet.text)

# indexable
last_snippet = fetched_transcript[-1]

# provides a length
snippet_count = len(fetched_transcript)
"""
def fetch_transcript(video_id):
    api = YouTubeTranscriptApi()
    try:
        logger.info("video: %s", video_id)
        fetched_transcript = api.fetch(video_id)
        transcript_text_list = []
        for snippet in fetched_transcript:
            transcript_text_list.append(snippet.text)

        transcript_text = ''.join(transcript_text_list)

        return transcript_text
        
    except (TranscriptsDisabled, NoTranscriptFound):
        logger.warning("No transcript available for video %s", video_id)
        return None
    except Exception as e:
        logger.error("Error fetching transcript for video %s: %s", video_id, e)
        return None
