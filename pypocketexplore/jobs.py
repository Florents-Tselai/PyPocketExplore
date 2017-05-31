__author__ = 'Florents Tselai'

import requests as req
from pymongo import MongoClient
from redis import StrictRedis
from rq import get_current_connection, Queue
from rq.decorators import job

from pypocketexplore import config
from pypocketexplore import logger
from pypocketexplore.config import API_BIND_URL
from pypocketexplore.parser import PocketTopicScraper


@job(config.TOPICS_QUEUE_NAME, connection=StrictRedis(config.REDIS_HOST, config.REDIS_PORT), timeout=10 * 24 * 3600,
     result_ttl=10 * 24 * 3600, ttl=10 * 24 * 3600)
def download_topic_items(topic_label,
                         limit,
                         parse,
                         log=logger):
    items_collection = MongoClient(config.MONGO_URI).get_default_database().get_collection(config.ITEMS_COLLECTION_NAME)
    redis_con = get_current_connection() if get_current_connection() else StrictRedis(config.REDIS_HOST,
                                                                                      config.REDIS_PORT)
    scraper = PocketTopicScraper(topic_label, limit, parse)
    topic_scraped = scraper.scrap()

    # Save scraped items
    if topic_scraped.items:
        log.info('Saving {} items to mongo'.format(len(topic_scraped.items)))
        items_collection.insert_many([item.to_dict() for item in topic_scraped.items])
    else:
        log.error('{} items downloaded for topic {}'.format(len(topic_scraped.items),
                                                            topic_scraped.label))
        raise Exception('No topics downloaded for topic {}'.format(topic_scraped.label))

    # Mark topic as scraped
    redis_con.sadd('pypocketexplore.scraped_topics', topic_label)

    for related_topic in topic_scraped.related_topics:
        is_in_queue = any(
            related_topic.label in job.args for job in Queue(config.TOPICS_QUEUE_NAME, connection=redis_con).get_jobs())
        if redis_con.sismember('pypocketexplore.scraped_topics', related_topic.label) or is_in_queue:
            pass
        else:
            log.info('Enqueuing related topic {}'.format(related_topic.label))
            resp = req.get('{}/api/topic/{}?async=true&parse=true'.format(API_BIND_URL, related_topic.label))
            log.info(resp.json())


if __name__ == '__main__':
    for topic in ['sex', 'love', 'music']:
        download_topic_items(topic, 10, True)
