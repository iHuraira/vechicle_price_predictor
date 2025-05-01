from exceptions import CustomError
import logger
import logging
from src.database.mongodb_connection import get_mongo_client, get_database
from src.database.mongodb_operations import (
    insert_document, find_documents, update_document
)

# Connect
client = get_mongo_client()
db = get_database(client)
cars_collection = db["cars"]

# Insert
insert_document(cars_collection, {"make": "Honda", "model": "Accord", "price": 9000})

# Find
cars = find_documents(cars_collection)
print(cars)

# Update
# update_document(cars_collection, {"make": "Honda"}, {"price": 16000})
