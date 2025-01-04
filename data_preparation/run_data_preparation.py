from save_video_data import save_video_data, save_to_json
from summarize_transcripts import summarize_transcript
from fetch_videos import fetch_videos_from_playlist, fetch_video_metadata
from fetch_trascripts import fetch_transcript
import sys
import os
# Add the root directory to sys.path
root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)


def run_data_preparation(all_sources):
    no_transcripts_videos = set()
    n_saved_videos = 0
    all_videos_metadata = []  # Consolidated list for all video metadata

    for source in all_sources:
        source_type = source.get("type")
        source_id = source.get("id")
        category = source.get("category")

        if source_type == "playlist":
            # Fetch videos from the playlist
            video_metadata_list = fetch_videos_from_playlist(
                source_id, category)
            all_videos_metadata.extend(
                video_metadata_list)  # Combine into the list

        elif source_type == "video":
            # Fetch metadata for a single video
            video_metadata = fetch_video_metadata(source_id, category)
            all_videos_metadata.append(video_metadata)  # Add to the list
        else:
            print(f"Unknown source type: {source_type} for ID: {source_id}")

    # Fetch transcripts for all videos
    for video_item in all_videos_metadata:
        video_id = video_item.get("video_id")

        if video_id:
            transcript_text, transcript_timestamp = fetch_transcript(video_id)
        else:
            print(f"Missing video_id in metadata: {video_item}")

        if transcript_text == "No transcript":
            no_transcripts_videos.add(video_id)
            print(f"Transcript not found for Video {video_id}")
            continue

        # summarize video
        exercises_summary, main_knowledge_summary = summarize_transcript(
            transcript_text, video_item.get("category"))

        # prepare data to save to db
        video_item['exercises_summary'] = exercises_summary
        video_item['main_knowledge_summary'] = main_knowledge_summary

        # save to json in case it fails to save to MongoDB
        print("Saving to JSON")
        save_to_json(video_id, video_item)

        # save to db
        print("Saving to MongoDB")
        save_video_data(video_item)

        n_saved_videos += 1
        print(f" {n_saved_videos} videos saved")

    return no_transcripts_videos  # if needed


all_sources = [{
    "type": "playlist",
    "id": "PLp4G6oBUcv8w8ujRtP5BtvJe8PXBwiTdl",  # jeff nippard tier lists
    "category": "tier_list"
}, {
    "type": "video",
    "id": "_gakDkB24WI",  # dr.mike glutes workout
    "category": "workout_session"
},
    {
    "type": "video",
    "id": "8zWDuWKdBZU",  # jeff nippard glutes workout
    "category": "workout_session"
},
]

run_data_preparation(all_sources)
