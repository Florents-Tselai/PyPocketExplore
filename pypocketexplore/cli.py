#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import json
import sys
from time import sleep

import click
import requests as req
from bs4 import BeautifulSoup
from pymongo import MongoClient

from pypocketexplore.parser import PocketTopicScraper, logger, InvalidTopicError, TooManyRequestsError


@click.group()
def cli():
    pass


@cli.command('topic', help='Download items for specific topics')
@click.argument('label', nargs=-1)
@click.option('--limit', default=100, help='Limit items to download')
@click.option('--out', default='pypocketexplore_output_topics.json', help='JSON output filepath')
@click.option('--nlp', is_flag=True, help='If set, also downloads the page and applies NLP (through NLTK)')
def topic(label, limit, out, nlp):
    items = []
    for l in label:
        scraper = PocketTopicScraper(l, limit=limit, parse=nlp)
        items.extend([i.to_dict() for i in scraper.scrap().items])
    json.dump(items,
              open(out, encoding='utf-8', mode='w'),
              indent=4,
              sort_keys=True
              )


@cli.command('batch', help='Download items for all topics recursively. \nUSE WITH CAUTION!')
@click.option('--n', default=sys.maxsize, help='Max number of total items to download')
@click.option('--limit', default=100, help='Limit items to download per topic')
@click.option('--out', default='pypocketexplore_output_topics.json', help='JSON output filepath')
@click.option('--nlp', is_flag=True, default=True, help='If set, also downloads the page and applies NLP (through NLTK)')
@click.option('--mongo', default='mongodb://localhost:27017/pypocketexplore', help='Mongo DB URI to save items')
def batch(limit=100, out='pypocketexplore_output_topics.json', n=sys.maxsize, nlp=True, mongo=None):
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
    if mongo:
        mongo_collection = MongoClient(mongo).get_default_database().get_collection('items')
        # Clear collection
        mongo_collection.remove({})

    logger.info(
        "Scraped {} | Remaining {} | Items {}".format(len(topics_already_scraped), len(topics_to_scrap), len(items)))
    while len(topics_to_scrap) > 0 and len(items) <= n:
        current_topic = topics_to_scrap.pop()
        logger.info("Working with topic {}".format(current_topic))

        try:
            scraper = PocketTopicScraper(current_topic, limit=limit, parse=nlp)

        except InvalidTopicError:
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
        if mongo:
            if topic_scraped.items:
                insert_results = mongo_collection.insert_many([i.to_dict() for i in topic_scraped.items],
                                                              bypass_document_validation=True)
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
