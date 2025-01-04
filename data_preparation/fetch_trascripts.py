
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)


def fetch_transcript(video_id):
    try:
        # Fetch transcript
        transcript_timestamp = YouTubeTranscriptApi.get_transcript(video_id)
        if transcript_timestamp:
            transcript_text = " ".join([part["text"]
                                       for part in transcript_timestamp])
            return transcript_text, transcript_timestamp
        return None, None
    except (TranscriptsDisabled, NoTranscriptFound):
        print(f"No transcript available for video {video_id}")
        return None, None
    except Exception as e:
        print(f"Error fetching transcript for video {video_id}: {e}")
        return None, None


