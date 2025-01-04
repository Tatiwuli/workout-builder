from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


API_SERVICE_NAME = "youtube"
API_VERSION = "v3"


def get_authenticated_service():
    """
    Authenticate and return the YouTube API service object using an API key.
    """
    try:
        # Build the YouTube API client
        service = build(API_SERVICE_NAME, API_VERSION,
                        developerKey=YOUTUBE_API_KEY)
        print("YouTube API service built successfully")
        return service
    except Exception as e:
        print(f"Error creating YouTube API service: {e}")
        raise


def get_videos_from_playlist(playlist_id, category):
    youtube_api = get_authenticated_service()

    videos_metadata_lst = []
    seen_videos = set()
    # previously summarized videos during testing
    seen_videos.add('spKGN0XzErU')
    seen_videos.add('c3pbe3qzatQ')
    seen_videos.add('kIXcoivzGf8')
    seen_videos.add('GNO4OtYoCYk')

    print(f"Processing playlist: {playlist_id}")
    next_page_token = None

    while True:  # iterate over the pages
        response = youtube_api.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,  # Max allowed by API
            pageToken=next_page_token
        ).execute()

        for item in response["items"]:

            snippet = item['snippet']
            video_id = snippet["resourceId"]["videoId"]

            # if we already stored the video_id
            if video_id in seen_videos:
                continue  # skip

            video_metadata_dict = {
                'playlist_id': playlist_id,
                'category': category,
                'video_id': video_id,
                'title': snippet['title'],
                'published_date': snippet['publishedAt'],
                'video_url': f"https://www.youtube.com/watch?v={video_id}",
                'thumbnail_img': snippet['thumbnails']['default']['url']

            }

            # keep track of stored videos to avoid duplicates
            seen_videos.add(video_id)
            # append the video metadata to final dict
            videos_metadata_lst.append(video_metadata_dict)

        # Handle pagination
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

        n_videos = len(seen_videos)
        print("Number of videos extracted: ", n_videos)

    return videos_metadata_lst


def get_transcript(video_id):
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


# test
#get all videos from a playlist
videos_metadata_lst = get_videos_from_playlist("PLp4G6oBUcv8w8ujRtP5BtvJe8PXBwiTdl", "tier_list")
print("Video metadata: ", videos_metadata_lst)
#get the first video item and its video_id
video_1 = videos_metadata_lst[0]
video_1_id = video_1.get("video_id")
#get the video's transcript 
transcript_text, transcript_timestamp = get_transcript(video_1_id)
print("Transcript text: \n", transcript_text)
print("Transcript with timestamps: \n", transcript_timestamp)

