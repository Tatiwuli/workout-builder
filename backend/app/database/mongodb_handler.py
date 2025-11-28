from pymongo import MongoClient, UpdateOne
from pymongo import MongoClient

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.results import InsertOneResult

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class WorkoutBuilderDatabaseHandler:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGODB_URI")
       
        if not self.mongo_uri:
            raise ValueError(
                "MONGODB_URI not found in environment or passed explicitly.")

        self.client = MongoClient(self.mongo_uri, server_api=ServerApi("1"))
        self.test_connection()
        self.db = self.client["workout_builder"]
        self.batch_size = 100
        self.timestamp_utc = datetime.now(timezone.utc)
        # Per-collection natural unique keys; extend as new collections are added
        self.unique_keys_by_collection: Dict[str, List[str]] = {
            "videos_summaries": ["video_id"],
            "wikis": ["wiki_name"],
        }
        self._ensure_unique_indexes()



    def apply_timestamps(self, doc: dict) -> dict:
        now = self.timestamp_utc
        if "created_at" not in doc:
            doc["created_at"] = now
        doc["updated_at"] = now
        return doc

    def _ensure_unique_indexes(self):
        for coll, fields in self.unique_keys_by_collection.items():
            collection = self.db[coll]
            for f in fields:
                try:
                    collection.create_index(f, unique=True)
                except Exception as e:
                    logger.warning(f"Unique index on {coll}.{f} may already exist: {e}")

    def _build_unique_filter(self, collection_name, data):
        fields = self.unique_keys_by_collection.get(collection_name)
        if not fields:
            return None
        if not all(field in data for field in fields):
            return None
        return {field: data[field] for field in fields}

    def test_connection(self):

        try:
            self.client.admin.command("ping")
            logger.info("Successfully connected to the MongoDB server.")
        except Exception as e:
            logger.error(f"Failed to connect to the MongoDB server: {e}")
            raise ConnectionError("Failed to connect to the MongoDB server.")

    def insert_one_data(self, collection_name, data) -> InsertOneResult:
        try:
            collection = self.db[collection_name]
            now = self.timestamp_utc
            filt = self._build_unique_filter(collection_name, data)

            if filt:
                update = {
                    "$set": {**data, "updated_at": now},
                    "$setOnInsert": {"created_at": now},
                }
                result = collection.update_one(filt, update, upsert=True)
                if result.matched_count > 0:
                    logger.info(f"Deduplicated and updated existing document in '{collection_name}' (filter={filt}).")
                elif result.upserted_id is not None:
                    logger.info(f"Inserted new document in '{collection_name}' via upsert (id={result.upserted_id}).")
                else:
                    logger.info(f"Upsert completed in '{collection_name}' (filter={filt}).")
                return result
            else:
                # No known unique key → do a normal insert with timestamps
                self.apply_timestamps(data)
                return collection.insert_one(data)
        except Exception as e:
            logger.error(f"Error inserting data into {collection_name}: {e}")
            return None

    def insert_many_data(self, collection_name, data_list):
        try:
            collection = self.db[collection_name]
            for data in data_list:
                now = self.timestamp_utc
                filt = self._build_unique_filter(collection_name, data)

                if filt:
                    update = {
                        "$set": {**data, "updated_at": now},
                        "$setOnInsert": {"created_at": now},
                    }
                    result = collection.update_one(filt, update, upsert=True)
                    if result.matched_count > 0:
                        logger.info(f"Deduplicated and updated existing document in '{collection_name}' (filter={filt}).")
                    elif result.upserted_id is not None:
                        logger.info(f"Inserted new document in '{collection_name}' via upsert (id={result.upserted_id}).")
                else:
                    self.apply_timestamps(data)
                    collection.insert_one(data)
        except Exception as e:
            logger.error(f"Error inserting batch data into {collection_name}: {e}")

    def fetch_data(self, collection_name, query):
        try:
            collection = self.db[collection_name]
            return list(collection.find(query))
        except Exception as e:
            logger.error(f"Error fetching data from {collection_name}: {e}")
            return []

    def delete_one_data(self, collection_name, query):
        try:
            collection = self.db[collection_name]
            return collection.delete_one(query)
        except Exception as e:
            logger.error(f"Error deleting data from {collection_name}: {e}")
            return None


    def delete_many_data(self, collection_name: str, filter_query: dict):
       
        collection = self.db[collection_name]
        result = collection.delete_many(filter_query)
        logger.info(f"Deleted {result.deleted_count} documents from '{collection_name}' collection.")
        return result.deleted_count
      
        
    def edit_field_name(self, collection_name: str, old_field_name: str, new_field_name: str, filter_query=None):
        try:
            collection = self.db[collection_name]

            # Default to updating all documents if no filter is provided
            if filter_query is None:
                filter_query = {}

            update_query = {
                "$rename": {old_field_name: new_field_name},
                "$set": {"updated_at": self.timestamp_utc}
            }

            result = collection.update_many(filter_query, update_query)

            logger.info(f"Renamed field '{old_field_name}' to '{new_field_name}' in {result.modified_count} documents in collection '{collection_name}'.")
            return result.modified_count

        except Exception as e:
            logger.error(f"Error renaming field '{old_field_name}' to '{ new_field_name}' in collection '{collection_name}': {e}")
            return 0

    def edit_field(self, collection_name: str, field_name: str, new_value, filter_query=None):
        
        try:
            collection = self.db[collection_name]

            # Default to updating all documents if no filter is provided
            if filter_query is None:
                filter_query = {}

            update_query = {"$set": {field_name: new_value, "updated_at": self.timestamp_utc}}

            result = collection.update_many(filter_query, update_query)

            logger.info(f"Modified {result.modified_count} documents in collection '{collection_name}'.")
            return result.modified_count

        except Exception as e:
            logger.error(f"Error updating field '{field_name}' in collection '{collection_name}': {e}")
            return 0
