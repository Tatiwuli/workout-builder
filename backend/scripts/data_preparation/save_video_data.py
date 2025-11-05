from app.database.mongodb_handler import WorkoutBuilderDatabaseHandler

import os 
import json
from datetime import datetime 


def save_video_data(video_item):
    mongodb_handler = WorkoutBuilderDatabaseHandler(
        database_name="workout_builder")

    mongodb_handler.insert_one_data("videos_summaries", video_item)
    print("Videos successfuly saved!")
    



def save_to_json(video_id, video_item):
   
    # define the path for json files
    db_file_path = os.path.join( "data", "json_summaries") #running from common root directory workout-builder
    os.makedirs(db_file_path, exist_ok=True)

    json_filename = f"info_{video_id}_{
        datetime.now().strftime('%Y%m%d%H%M')}.json"
    json_filepath = os.path.join(db_file_path, json_filename)

    # Save the data to JSON file
    try:
        with open(json_filepath, 'w', encoding='utf-8') as json_file:
            json.dump(video_item, json_file, indent=4, ensure_ascii=False)
        print(f"Saved video information to JSON: {json_filepath}")
    except Exception as e:
        print(f"Failed to save video {video_id} information to JSON: {e}")
