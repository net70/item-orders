from pymongo import MongoClient, UpdateOne
from decouple import config

# Connect to one of the MongoDB containers
mongo_client = MongoClient(config('MONGODB_SERVER'), replicaSet="rs0")
