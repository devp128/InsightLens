from pymongo import MongoClient
from os import getenv
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = getenv('MONGO_URI', 'mongodb://localhost:27017')
MONGO_DB = getenv('MONGO_DB', 'wealth_db')

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

# Example: db['clients'].find_one({})
