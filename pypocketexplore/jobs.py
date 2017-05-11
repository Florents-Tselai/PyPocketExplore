import requests as req
from time import sleep
from random import choice
from config import MONGO_URI
from pymongo import MongoClient

def extract_topic_items(topic):
    db = MongoClient(MONGO_URI).get_default_database()
    resp = req.get('http://localhost:5000/api/topic/{}'.format(topic))

    items = resp.json()
    if items:
        res = db['items'].insert(resp.json())
        sleep(60)
        return res
    else:
        raise Exception
