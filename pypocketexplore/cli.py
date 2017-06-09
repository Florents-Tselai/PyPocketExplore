__author__ = 'Florents Tselai'

import json
from logging import ERROR

import click
import requests as req
from bs4 import BeautifulSoup
from pypocketexplore.parser import PocketTopicScraper, logger, InvalidTopicException, TooManyRequestsError
from time import sleep


@click.group()
def cli():
    pass


@cli.command('topic')
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


@cli.command('batch')
@click.option('--limit', default=100, help='Limit items to download')
@click.option('--out', default='topics.json', help='JSON output fp')
@click.option('--parse', is_flag=True, help='If set, also parses the html and runs it through NLTK')
def batch(limit, out, parse):
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

    logger.info("Scraped {} | Remaining {} | Items {}".format(len(topics_already_scraped), len(topics_to_scrap), len(items)))
    while len(topics_to_scrap) > 0:
        current_topic = topics_to_scrap.pop()

        try:
            scraper = PocketTopicScraper(current_topic, limit=limit, parse=parse)

        except InvalidTopicException:
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

        for related in topic_scraped.related_topics:
            if related.label not in topics_already_scraped:
                topics_to_scrap.add(related.label)

        topics_already_scraped.add(current_topic)
        logger.info("Scraped {} | Remaining {} | Items {}".format(len(topics_already_scraped), len(topics_to_scrap),
                                                                 len(items)))

    json.dump(items, open(out, encoding='utf-8', mode='w'),
              indent=4,
              sort_keys=True)



