import os

from pymongo import MongoClient

MONGO_URI = os.getenv('MONGO_URI')
MONGO_DATABASE = os.getenv('MONGO_DATABASE')

client = MongoClient(MONGO_URI)
db = client[MONGO_DATABASE]
