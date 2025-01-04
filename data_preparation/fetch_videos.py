from googleapiclient.discovery import build
import os
from dotenv import load_dotenv


load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
assert YOUTUBE_API_KEY, "YOUTUBE API KEY not provided"


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

youtube_service = get_authenticated_service()


def fetch_video_metadata(video_id,category):
    
    try:
        # Fetch video details using the Videos API
        video_response = youtube_service.videos().list(
            part="snippet",
            id=video_id
        ).execute()
    except Exception as e:
        print(f"Error fetching video details for {video_id}: {e}")
        print(video_response)
        return None
        
    # Extract video details from the response
    video_items = video_response.get("items", [])
    if not video_items:
        print(f"No details found for video_id: {video_id}")
        return None

    video_data = video_items[0].get("snippet", {})

    # Build the output dictionary
    video_info = {
        "playlist_id": None, 
        "category": category,    
        "video_id": video_id,
        "title": video_data.get("title"),
        "published_date": video_data.get("publishedAt"),
        "video_url": f"https://www.youtube.com/watch?v={video_id}",
        "thumbnail_img": video_data.get("thumbnails", {}).get("high", {}).get("url")
    }

    return video_info

        


def fetch_videos_from_playlist(playlist_id, category):
   
    videos_metadata_lst = []
    seen_videos = set()
    
    
    print(f"Processing playlist: {playlist_id}")
    next_page_token = None

    while True:  # iterate over the pages
        response = youtube_service.playlistItems().list(
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

