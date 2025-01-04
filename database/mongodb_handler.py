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

