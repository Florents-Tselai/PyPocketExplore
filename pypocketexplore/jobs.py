from redis import StrictRedis
from rq import get_current_connection, Queue
from rq.decorators import job
from pymongo import MongoClient
from pypocketexplore import config
from pypocketexplore.parser import *


@job(config.TOPICS_QUEUE_NAME, connection=StrictRedis(), timeout=10*24*3600, result_ttl=10*24*3600, ttl=10*24*3600)
def download_topic_items(topic_label, limit, parse):
    items_collection = MongoClient(config.MONGO_URI).get_default_database().get_collection(config.ITEMS_COLLECTION_NAME)
    redis_con = get_current_connection()
    topic = PocketTopic(topic_label)
    PocketTopicScraper(topic, limit, items_collection, parse)

    redis_con.sadd('pypocketexplore.scraped_topics', topic_label)

    for related_topic in topic.related_topics:
        is_in_queue = any(related_topic in job.args for job in Queue(config.TOPICS_QUEUE_NAME, connection=redis_con).get_jobs())
        if redis_con.sismember('pypocketexplore.scraped_topics', related_topic) or is_in_queue:
            pass
        else:
            resp = req.get('http://localhost:5000/api/topic/{}?async=true'.format(related_topic.label))
            print('Enqueuing related topic {}'.format(related_topic.label))