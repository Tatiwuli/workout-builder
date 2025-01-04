from bson import ObjectId  # For working with MongoDB ObjectIds
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.results import InsertOneResult

import os
import json
from dotenv import load_dotenv

load_dotenv()

class WorkoutBuilderDatabaseHandler:
    def __init__(self, database_name: str):
        
        MONGO_URI = os.getenv("MONGODB_URI")
        assert MONGO_URI, "MongoDB URI not provided!"
        self.client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
        self.test_connection()
        self.db = self.client[database_name]
        self.batch_size = 100

    def test_connection(self):

        try:
            self.client.admin.command("ping")
            print("Successfully connected to the MongoDB server.")
        except Exception as e:
            print(f"Failed to connect to the MongoDB server: {e}")
            raise ConnectionError("Failed to connect to the MongoDB server.")

    def insert_one_data(self, collection_name, data) -> InsertOneResult:
        try:
            collection = self.db[collection_name]
            return collection.insert_one(data)
        except Exception as e:
            print(f"Error inserting data into {collection_name}: {e}")
            return None

    def insert_many_data(self, collection_name, data_list):
        try:
            collection = self.db[collection_name]
            for i in range(0, len(data_list), self.batch_size):
                batch = data_list[i: i + self.batch_size]
                collection.insert_many(batch)
        except Exception as e:
            print(f"Error inserting batch data into {collection_name}: {e}")

    def fetch_data(self, collection_name, query):
        try:
            collection = self.db[collection_name]
            return list(collection.find(query))
        except Exception as e:
            print(f"Error fetching data from {collection_name}: {e}")
            return []

    def delete_one_data(self, collection_name, query):
        try:
            collection = self.db[collection_name]
            return collection.delete_one(query)
        except Exception as e:
            print(f"Error deleting data from {collection_name}: {e}")
            return None


    def delete_many_data(self, collection_name: str, filter_query: dict):
       
        collection = self.db[collection_name]
        result = collection.delete_many(filter_query)
        print(f"Deleted {result.deleted_count} documents from '{collection_name}' collection.")
        return result.deleted_count
      
        
    def edit_field_name(self, collection_name: str, old_field_name: str, new_field_name: str, filter_query=None):
        try:
            collection = self.db[collection_name]

            # Default to updating all documents if no filter is provided
            if filter_query is None:
                filter_query = {}

            update_query = {
                "$rename": {old_field_name: new_field_name}
            }

            result = collection.update_many(filter_query, update_query)

            print(f"Renamed field '{old_field_name}' to '{new_field_name}' in {
                  result.modified_count} documents in collection '{collection_name}'.")
            return result.modified_count

        except Exception as e:
            print(f"Error renaming field '{old_field_name}' to '{ new_field_name}' in collection '{collection_name}': {e}")
            return 0

    def edit_field(self, collection_name: str, field_name: str, new_value, filter_query=None):
        
        try:
            collection = self.db[collection_name]

            # Default to updating all documents if no filter is provided
            if filter_query is None:
                filter_query = {}

            update_query = {"$set": {field_name: new_value}}

            result = collection.update_many(filter_query, update_query)

            print(f"Modified {result.modified_count} documents in collection '{
                  collection_name}'.")
            return result.modified_count

        except Exception as e:
            print(f"Error updating field '{
                  field_name}' in collection '{collection_name}': {e}")
            return 0


wiki_mfitness_level = {
    "wiki": {
        "name": "wiki_by_fitness_level",
        "fitness_levels": [
            {
                "level": "beginners",
                "rationale": "Emphasis on learning proper technique and progressive overload, prioritizing form over volume.",
                "exercise_selection": [
                    "Prioritize movements that target multiple muscle groups (e.g., squats, pull-ups) to maximize efficiency and skill development.",
                    "Emphasize compound movements over isolation exercises."
                ],
                "n_exercises": "1-2 exercises per muscle group per session.",
                "sets": "3-6 sets total for the muscle group (e.g., 3 sets of a single exercise or 2 sets for each of 2 exercises).",
                "reps": "6-12 per set for compound lifts to focus on strength and hypertrophy; up to 15 for isolation movements if used sparingly.",
                "time_constraints": {
                    "short": [
                        "Avoid dropsets to minimize recovery demands.",
                        "Prioritize movements that can target multiple muscle parts.",
                        "Rest periods: 30-60 seconds between sets.",
                        "Use supersets with antagonist movements (e.g., push-ups + rows)."
                    ],
                    "medium": [
                        "Include 2 compound exercises and 1 isolation exercise per session.",
                        "Rest: 60 seconds for compound lifts; 30-60 seconds for isolation.",
                        "Use moderate weights (60-75% of 1RM)."
                    ],
                    "long": [
                        "Add more isolation exercises for muscle refinement.",
                        "Rest: 90 seconds for compound movements; 30-60 seconds for isolation.",
                        "Supersets can be added to improve session efficiency."
                    ]
                }
            },
            {
                "level": "intermediate_early",
                "rationale": "Experiment with volume, progressive overload using weight and reps, and rotating exercises periodically to prevent plateaus.",
                "exercise_selection": [
                    "Combine compound lifts with targeted isolation exercises."
                ],
                "n_exercises": "2-3 exercises per muscle group per session.",
                "sets": "6-10 sets total for the muscle group (e.g., 4-5 sets for a primary exercise and 2-3 sets for a secondary exercise).",
                "reps": "6-12 for compound lifts; 8-15 for isolation movements.",
                "time_constraints": {
                    "short": [
                        "Use supersets for antagonistic movements to save time.",
                        "Focus on 1-2 compound exercises and minimal isolation work.",
                        "Rest: 30-60 seconds between supersets."
                    ],
                    "medium": [
                        "Combine 2 compound exercises and 1-2 isolation exercises.",
                        "Rest: 60-90 seconds for compound lifts; 30-60 seconds for isolation.",
                        "Supersets can be used to balance efficiency and volume."
                    ],
                    "long": [
                        "Introduce dropsets for stubborn muscle groups or isolation exercises (apply only to the last set).",
                        "Rest: 90 seconds for compound lifts; 60 seconds for isolation movements.",
                        "Incorporate additional isolation exercises for refinement."
                    ]
                }
            },
            {
                "level": "intermediate_late",
                "rationale": "Advanced trainees may need higher intensity and volume to stimulate gains. Specialized techniques (e.g., supersets, dropsets, or myo-reps) can help push through plateaus.",
                "exercise_selection": [
                    "Sometimes emphasizing specialization phases to target lagging body parts."
                ],
                "n_exercises": "2-3 exercises per muscle group per session.",
                "sets": "10-12 total sets or more for specialization, depending on recovery and goals.",
                "reps": "6-12 for compound lifts; up to 20 for isolation exercises, depending on the phase and technique used (e.g., dropsets).",
                "time_constraints": {
                    "short": [
                        "Focus on compound exercises with higher rep ranges (10-15) to maximize time efficiency.",
                        "Supersets should dominate the workout structure.",
                        "Rest: 30-60 seconds between supersets."
                    ],
                    "medium": [
                        "Combine 2 compound exercises and 1-2 isolation exercises.",
                        "Use moderate rest intervals (60-90 seconds).",
                        "Dropsets can be selectively introduced for isolation exercises."
                    ],
                    "long": [
                        "Combine 2-3 compound exercises with 2-3 isolation exercises per muscle group.",
                        "Use advanced techniques like dropsets on the last set of isolation exercises.",
                        "Rest: 90 seconds for compound lifts; 60 seconds for isolation movements."
                    ]
                }
            }
        ]
    }
}


db = WorkoutBuilderDatabaseHandler("workout_builder")
db.insert_one_data("wikis", wiki_mfitness_level)