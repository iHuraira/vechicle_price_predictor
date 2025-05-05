import json

from logger import logging
from exceptions import CustomError

from src.database.mongodb_operations import insert_many_documents
from src.database.mongodb_connection import get_mongo_client, get_database
from src.database.mongodb_operations import insert_many_documents

class MongoDataPusher:
    def __init__(self, train_data, test_data, train_collection_name, test_collection_name, db_name="car_price_db"):
        self.train_data = train_data
        self.test_data = test_data
        self.train_collection_name = train_collection_name
        self.test_collection_name = test_collection_name
        self.db_name = db_name

        try:
            self.client = get_mongo_client()
            self.db = get_database(self.client, db_name)
            self.train_collection = self.db[train_collection_name]
            self.test_collection = self.db[test_collection_name]
            logging.info(f"Connected to MongoDB database: {db_name}")
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise CustomError(str(e))

    def _get_json_size_mb(self, data):
        json_str = json.dumps(data)
        size_bytes = len(json_str.encode('utf-8'))
        return round(size_bytes / (1024 * 1024), 2)

    def data_pusher(self):
        try:
            train_json = self.train_data.drop_duplicates().to_dict(orient='records')
            test_json = self.test_data.drop_duplicates().to_dict(orient='records')

            train_size = self._get_json_size_mb(train_json)
            test_size = self._get_json_size_mb(test_json)

            logging.info(f"Train data: {len(train_json)} records, approx {train_size} MB")
            logging.info(f"Test data: {len(test_json)} records, approx {test_size} MB")

            insert_many_documents(self.train_collection, train_json)
            insert_many_documents(self.test_collection, test_json)
            logging.info("Train and test data successfully inserted into MongoDB.")

        except Exception as e:
            logging.error(f"Error during MongoDB insertion: {e}")
            raise CustomError(str(e))
