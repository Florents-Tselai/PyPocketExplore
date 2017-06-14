__author__ = 'Florents Tselai'

import json
from time import sleep
import sys

import click
import requests as req
from bs4 import BeautifulSoup
from pymongo import MongoClient

from pypocketexplore.parser import PocketTopicScraper, logger, InvalidTopicException, TooManyRequestsError


@click.group()
def cli():
    pass


@cli.command('topic', help='Download for specific labels')
@click.argument('label', nargs=-1)
@click.option('--limit', default=100, help='Limit items to download')
@click.option('--out', default='topics.json', help='JSON output fp')
@click.option('--parse', is_flag=True, help='If set, also parses the html and runs it through NLTK')
def topic(label, limit, out, parse):
    items = []
    for l in label:
        scraper = PocketTopicScraper(l, limit=limit, parse=parse)
        items.extend([i.to_dict() for i in scraper.scrap().items])
    json.dump(items, open(out, encoding='utf-8', mode='w'),
              indent=4,
              sort_keys=True)


@cli.command('batch', help='Download topics recursively')
@click.option('--n', default=sys.maxsize, help='Max number of items')
@click.option('--limit', default=100, help='Limit items to download per topic')
@click.option('--out', default='topics.json', help='JSON output fp')
@click.option('--parse', is_flag=True, default=True, help='If set, also parses the html and runs it through NLTK')
@click.option('--mongo', default='mongodb://localhost:27017/pypocketexplore')
def batch(limit=100, out='topics.json', n=sys.maxsize, parse=True, mongo='mongodb://localhost:27017/pypocketexplore'):
    html = req.get(
        "https://www.ibm.com/watson/developercloud/doc/natural-language-understanding/categories.html").content
    soup = BeautifulSoup(html, 'html.parser')
    topics_to_scrap = set()
    for td in soup.find_all('td'):
        if td.text:
            topics_to_scrap.add(td.text)
            for t in td.text.split(' '):
                topics_to_scrap.add(t)

    topics_already_scraped = set()
    items = []
    mongo_collection = MongoClient(mongo).get_default_database().get_collection('items')
    # Clear collection
    mongo_collection.remove({})

    logger.info(
        "Scraped {} | Remaining {} | Items {}".format(len(topics_already_scraped), len(topics_to_scrap), len(items)))
    while len(topics_to_scrap) > 0 and len(items) <= n:
        current_topic = topics_to_scrap.pop()
        logger.info("Working with topic {}".format(current_topic))

        try:
            scraper = PocketTopicScraper(current_topic, limit=limit, parse=parse)

        except InvalidTopicException:
            logger.warning('Invalid topic %s' % current_topic)
            topics_already_scraped.add(current_topic)
            continue

        except TooManyRequestsError:
            logger.warning('Going to sleep for 1 hour')
            topics_to_scrap.add(current_topic)
            sleep(1 * 3600)
            logger.info('Woke up!')
            continue

        topic_scraped = scraper.scrap()
        items.extend([i.to_dict() for i in topic_scraped.items])
        if topic_scraped.items:
            insert_results = mongo_collection.insert_many([i.to_dict() for i in topic_scraped.items], bypass_document_validation=True)
            logger.info("{} items inserted to mongo".format(len(insert_results.inserted_ids)))

        for related in topic_scraped.related_topics:
            if related.label not in topics_already_scraped:
                topics_to_scrap.add(related.label)

        topics_already_scraped.add(current_topic)
        logger.info("Scraped {} | Remaining {} | Items {}".format(len(topics_already_scraped),
                                                                  len(topics_to_scrap),
                                                                  len(items))
                    )

    json.dump(items, open(out, encoding='utf-8', mode='w'),
              indent=4,
              sort_keys=True)

if __name__ == '__main__':
    batch()