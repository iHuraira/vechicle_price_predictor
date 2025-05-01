import os
from urllib.parse import quote_plus
from pymongo import MongoClient
from dotenv import load_dotenv
from src.utils.utils import load_config

# Load .env file
load_dotenv()
config = load_config()
mongo_cfg = config["mongodb"]

def get_mongo_client():
    username = quote_plus(os.getenv("MONGO_USERNAME"))
    password = quote_plus(os.getenv("MONGO_PASSWORD"))
    uri = mongo_cfg["uri"].format(username=username, password=password)

    return MongoClient(uri)


def get_database(client, db_name="car_price_db"):
    return client[db_name]
