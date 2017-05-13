from datetime import datetime

import requests as req
from pymongo import MongoClient

from pypocketexplore.config import MONGO_URI
from time import sleep
from redis import StrictRedis
import rq


def extract_topic_items(topic):
    r = StrictRedis()

    def topic_in_queue(topic):
        q = rq.Queue('topics', connection=StrictRedis())
        if any(job.kwargs.get('topic') for job in q.get_jobs()):
            return True
        else:
            return False

    db = MongoClient(MONGO_URI).get_default_database()
    resp = req.get('http://localhost:5000/api/topic/{}'.format(topic))
    data = resp.json()
    related_topics = data.get('related_topics')

    items = data.get('items')

    if resp.ok:
        print('Inserting {} items for topic {}'.format(len(items)), topic)
        res = db['items'].insert(items)
        r.sadd('scraped_topics', topic)

        for related_topic in related_topics:
            if not topic_in_queue(related_topic) and not r.sismember('scraped_topics', related_topic):
                print('Enqueuing related topic'.format(related_topic))
                req.get('http://localhost:5000/api/topic/{}?async=true'.format(related_topic)).json()
        print("Rate limit! Going to sleep for 2 mins!")
        sleep(2 * 60)
        print("Wakey wakey eggs and bakey!")
        return res

    else:
        raise Exception('Something went wrong with topic {}. /api/explore/{} returned {}'.format(topic, topic, resp))


if __name__ == '__main__':
    extract_topic_items('finance')
