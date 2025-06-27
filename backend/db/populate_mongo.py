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
    {
        "name": "Alice",
        "risk": "High",
        "age": 45,
        "city": "Mumbai",
        "preferences": ["tech", "banking"]
    },
    {
        "name": "Bob",
        "risk": "Low",
        "age": 52,
        "city": "Delhi",
        "preferences": ["energy", "auto"]
    },
    {
        "name": "Charlie",
        "risk": "Medium",
        "age": 38,
        "city": "Bangalore",
        "preferences": ["tech", "pharma"]
    },
    {
        "name": "Deepika",
        "risk": "High",
        "age": 41,
        "city": "Pune",
        "preferences": ["pharma", "tech"]
    },
    {
        "name": "Amitabh",
        "risk": "High",
        "age": 60,
        "city": "Mumbai",
        "preferences": ["tech", "auto"]
    },
    {
        "name": "Priya",
        "risk": "Low",
        "age": 35,
        "city": "Chennai",
        "preferences": ["banking", "energy"]
    }
])

print("MongoDB clients collection populated!")
