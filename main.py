# from exceptions import CustomError
# import logger
# import logging
# from src.database.mongodb_connection import get_mongo_client, get_database
# from src.database.mongodb_operations import (
#     insert_document, find_documents, update_document
# )

# # Connect
# client = get_mongo_client()
# db = get_database(client)
# cars_collection = db["cars"]

# # Insert
# insert_document(cars_collection, {"make": "Honda", "model": "Accord", "price": 9000})

# # Find
# cars = find_documents(cars_collection)
# print(cars)

# # Update
# # update_document(cars_collection, {"make": "Honda"}, {"price": 16000})

from src.etl_components.extract_csv import CSVExtractor
from src.etl_components.transform_clean import CSVTransformer
from src.etl_components.load_to_mongo import MongoDataPusher

if __name__ == "__main__":
    
    # ETL : 1. CSV Extraction
    extractor = CSVExtractor()
    train_data, test_data = extractor.extract_csv()

    # ETL : 2. Transformation
    transformer = CSVTransformer(train_data, test_data)
    transformed_train_data, transformed_test_data = transformer.transform()
    
    # ETL : 3. Load To Mongo
    mongo_data_pusher = MongoDataPusher(
        transformed_train_data, transformed_test_data,
        train_collection_name="train_data",
        test_collection_name="test_data",
        db_name="car_price_db"
    )
    mongo_data_pusher.data_pusher()
