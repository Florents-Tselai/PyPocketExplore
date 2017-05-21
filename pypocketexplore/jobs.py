from datetime import datetime

import requests as req
from pymongo import MongoClient

from pypocketexplore.config import MONGO_URI
from time import sleep
from redis import StrictRedis
import rq

import redis
from threading import Thread
import pickle
from newspaper import Article
from collections import deque
from queue import Queue
from time import time
import requests as req

from rq.decorators import job


@job('pocket.download', connection=redis.StrictRedis(), timeout=-1)
def download_item(item_id, item_url, redis_con=redis.StrictRedis()):
    item = {
        'item_id': item_id,
        'item_url': item_url
    }
    data = {
        'item_id': item.get('item_id'),
        'item_url': item.get('item_url'),
        'response': None,
        'article': None
    }

    try:
        # Make request
        data['response'] = req.get(data.get('item_url'))

        # Download article
        try:
            a = Article(item_url)
            data['article'] = a
            a.download()
            a.parse()
        except Exception as e:
            print('Item: {} | Url: {} | {}'.format(data.get('item_id'), data.get('item_url'), e))
            raise e

        redis_con.set('pocket:item:{}'.format(item.get('item_id')),
                           pickle.dumps(data)
                           )

    except Exception as e:
        print('Item: {} | Url: {} | {}'.format(data.get('item_id'), data.get('item_url'), e))
        raise e


def extract_topic_items(topic):
    r = StrictRedis()

    def topic_in_queue(topic):
        q = rq.Queue('topics', connection=StrictRedis())
        if any(job.kwargs.get('topic') == topic for job in q.get_jobs()):
            return True
        else:
            return False

    db = MongoClient(MONGO_URI).get_default_database()
    resp = req.get('http://localhost:5000/api/topic/{}'.format(topic))
    print(resp.content)
    data = resp.json()
    related_topics = data.get('related_topics')

    items = data.get('items')

    if resp.ok:
        if len(items) > 0:
            print('Inserting {} items for topic {}'.format(len(items), topic))
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
            print('No items for topic {}'.format(topic))

    else:
        raise Exception('Something went wrong with topic {}. /api/explore/{} returned {}'.format(topic, topic, resp))


if __name__ == '__main__':
    extract_topic_items('finance')
