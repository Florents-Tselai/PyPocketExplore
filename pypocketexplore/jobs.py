import requests as req
from redis import StrictRedis
from rq import get_current_connection
from rq.decorators import job

from pypocketexplore.config import ITEMS_COLLECTION, TOPICS_QUEUE
from pypocketexplore.parser import *


@job('pocket.topics', connection=StrictRedis(), timeout=10*24*3600, result_ttl=10*24*3600, ttl=10*24*3600)
def download_topic_items(topic_label):
    redis_con = get_current_connection()
    topic = PocketTopic(topic_label)
    PocketTopicScraper(topic, collection=ITEMS_COLLECTION, parse=True)

    redis_con.sadd('pocket.scraped_topics', topic_label)

    for related_topic in topic.related_topics:
        if redis_con.sismember('pocket.scraped_topics', related_topic) or any(related_topic in job.args for job in TOPICS_QUEUE.get_jobs()):
            pass
        else:
            resp = req.get('http://localhost:5000/api/topic/{}?async=true'.format(related_topic.label))
            print('Enqueuing related topic {}'.format(related_topic.label))

if __name__ == '__main__':
    pass