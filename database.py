from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"

client = MongoClient(MONGO_URI)
db = client["chat_app"]

users_collection = db["users"]
messages_collection = db["messages"]
