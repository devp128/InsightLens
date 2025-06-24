import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

clients_collection = db.clients

clients_collection.delete_many({})  # Clean slate
clients_collection.insert_many([
    {"name": "Alice", "segment": "wealth", "city": "Mumbai"},
    {"name": "Bob", "segment": "wealth", "city": "Delhi"},
    {"name": "Charlie", "segment": "wealth", "city": "Bangalore"}
])

print("MongoDB clients collection populated!")
