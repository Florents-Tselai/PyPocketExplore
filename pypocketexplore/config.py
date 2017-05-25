from pymongo import MongoClient
from redis import StrictRedis
from rq import Queue

MONGO_URI = 'mongodb://localhost:27017/pocket-topics'
db = MongoClient(MONGO_URI).get_default_database()
redis = StrictRedis()

ITEMS_COLLECTION = db.get_collection('pocket.items')
TOPICS_COLLECTION = db.get_collection('pocket.topics')
ITEMS_QUEUE = Queue('pocket.items', connection=StrictRedis())
TOPICS_QUEUE = Queue('pocket.topics', connection=StrictRedis())