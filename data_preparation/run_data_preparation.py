
from fetch_trascripts import fetch_trascript
from fetch_videos import fetch_videos_from_playlist

def fetch_videos_transcripts(playlist_id, category):
    # get all videos from a playlist
    videos_metadata_lst = fetch_videos_from_playlist(playlist_id, category)
    print("Video metadata: ", videos_metadata_lst[:3])

    # get the first video item and its video_id
    for video_item in videos_metadata_lst:
        video_id = video_item.get("video_id")

        # get the video's transcript
        transcript_text, transcript_timestamp = fetch_trascript(video_id)
        print("Transcript text: \n", transcript_text[:10])
        print("Transcript with timestamps: \n", transcript_timestamp[:10])


# test
fetch_videos_transcripts('PLp4G6oBUcv8w8ujRtP5BtvJe8PXBwiTdl', 'tier_list')
