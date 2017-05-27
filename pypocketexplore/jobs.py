from redis import StrictRedis
from rq import get_current_connection, Queue
from rq.decorators import job
from pymongo import MongoClient
from pypocketexplore import config
from pypocketexplore.parser import PocketTopicScraper
import requests as req
import logging

# create logger with ''
logger = logging.getLogger('pypocketexplore.jobs')
logger.setLevel(logging.INFO)
# create file handler which logs even debug messages
fh = logging.FileHandler('pypocketexplore.jobs.log')
fh.setLevel(logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)
log = logger


@job(config.TOPICS_QUEUE_NAME, connection=StrictRedis(config.REDIS_HOST, config.REDIS_PORT), timeout=10*24*3600, result_ttl=10*24*3600, ttl=10*24*3600)
def download_topic_items(topic_label, limit, parse):
    items_collection = MongoClient(config.MONGO_URI).get_default_database().get_collection(config.ITEMS_COLLECTION_NAME)
    redis_con = get_current_connection() if get_current_connection() else StrictRedis(config.REDIS_HOST, config.REDIS_PORT)
    scraper = PocketTopicScraper(topic_label, limit, parse)
    topic_scraped = scraper.scrap()

    # Save scraped items
    if topic_scraped.items:
        log.info('Saving {} items to mongo'.format(len(topic_scraped.items)))
        items_collection.insert_many([item.to_dict() for item in topic_scraped.items])
    else:
        log.exception('{} items downloaded for topic {}'.format(len(topic_scraped.items),
                                                              topic_scraped.label))
        raise Exception('No topics downloaded for topic {}'.format(topic_scraped.label))


    # Mark topic as scraped
    redis_con.sadd('pypocketexplore.scraped_topics', topic_label)

    for related_topic in topic_scraped.related_topics:
        is_in_queue = any(related_topic.label in job.args for job in Queue(config.TOPICS_QUEUE_NAME, connection=redis_con).get_jobs())
        if redis_con.sismember('pypocketexplore.scraped_topics', related_topic.label) or is_in_queue:
            pass
        else:
            log.info('Enqueuing related topic {}'.format(related_topic.label))
            resp = req.get('http://localhost:5000/api/topic/{}?async=true&parse=true'.format(related_topic.label))
            log.info(resp.json())

if __name__ == '__main__':
    for topic in ['sex', 'love', 'music']:
        download_topic_items(topic, 10, True)

