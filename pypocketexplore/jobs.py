from datetime import datetime

import requests as req
from pymongo import MongoClient

from pypocketexplore.config import MONGO_URI
from time import sleep

def extract_topic_items(topic):
    db = MongoClient(MONGO_URI).get_default_database()
    data = req.get('http://localhost:5000/api/topic/{}'.format(topic)).json()
    related_topics = data.get('related_topics')

    items = data.get('items')

    if items:
        res = db['items'].insert(items)
        db['topics'].update_many({'topic': topic}, {'$set': {'topic': topic,
                                                             'is_scraped': True,
                                                             'datetime_scraped': datetime.utcnow(),
                                                             'queued': True}},
                                 upsert=True)
        for related_topic in related_topics:
            req.get('http://localhost:5000/api/topic/{}?async=true'.format(topic)).json()
        sleep(2 * 60)
        return res
    else:
        raise Exception


if __name__ == '__main__':
    extract_topic_items('finance')
