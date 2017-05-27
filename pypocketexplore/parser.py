#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

__author__ = 'Florents Tselai'

from pprint import pprint

import requests as req
from bs4 import BeautifulSoup
from datetime import datetime
from newspaper import Article, ArticleException
from tqdm import tqdm
from pymongo import MongoClient
import logging

from pypocketexplore.model import PocketItem, PocketTopic
from pypocketexplore.config import MONGO_URI, ITEMS_COLLECTION_NAME

print = pprint

# create logger with ''
logger = logging.getLogger('pypocketexplore.parser')
logger.setLevel(logging.INFO)
# create file handler which logs even debug messages
fh = logging.FileHandler('pypocketexplore.parser.log')
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


class PocketArticleDownloader:
    ARTICLE_ATTRIBUTES_TO_KEEP = [
        'title',
        'text',
        'top_img',
        'meta_keywords',
        'summary',
        'additional_data',
        'source_url',
        'keywords',
        'meta_img',
        'publish_date',
        'meta_favicon',
        'movies',
        'tags',
        'authors',
        'images',
        'meta_description'
    ]

    def __init__(self, pocket_item):
        self._pocket_item = pocket_item

    def download(self):
        try:
            article = Article(self._pocket_item.url)
            article.download()
            article.parse()
            article.nlp()

            article.tags = list(article.tags)
            if article.publish_date:
                article.publish_date = article.publish_date.timestamp()

            article.images = list(article.images)

            return dict((k, v) for k, v in article.__dict__.items()
                        if k in self.ARTICLE_ATTRIBUTES_TO_KEEP
                        )
        except ArticleException:
            log.warning('Could not download article for {}'.format(self._pocket_item.url))
            return {}


class PocketTopicScraper:
    def __init__(self, topic_label,
                 limit=None,
                 parse=False):
        if isinstance(topic_label, str):
            self._topic_label = topic_label
        else:
            raise TypeError('Can only pass str')

        self.limit = limit
        self.parse = parse
        log.info('Topic {} | limit {} | parse {}'.format(topic_label, self.limit, self.parse))

    def _make_request(self):
        html = req.get("http://getpocket.com/explore/{}".format(self._topic_label), headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }).content

        return html

    def scrap(self):
        html = self._make_request()
        utc_now = datetime.utcnow().timestamp()
        soup = BeautifulSoup(html, 'html.parser')

        data_ids = [a.get('data-id') for a in soup.find_all('a', class_='link_track')]
        titles = [a.text for a in soup.find_all('a', class_='link_track') if a.text != '\n \n']
        excerpts = [p.text for p in soup.find_all('p', class_='excerpt')]
        saves_counts = [int(a.text.replace(' saves', '').replace(',', '')) for a in
                        soup.find_all('div', class_='save_count')]
        images = [div.get('data-thumburl') for div in soup.find_all('div', class_='item_image')]

        pocket_items = []
        related_topics_labels = []
        for item_id, title, excerpt, saves_count, image in tqdm(
                zip(data_ids[1::2], titles, excerpts, saves_counts, images)):
            if self.limit and len(pocket_items) >= self.limit:
                break
            log.info('Downloading item {}'.format(item_id))
            current_item = PocketItem(item_id)
            pocket_items.append(current_item)

            current_item.url = soup.find('a', attrs={'data-id': item_id}).get('data-saveurl')
            current_item.title = title
            current_item.excerpt = excerpt
            current_item.saves_count = saves_count
            current_item.topic = self._topic_label.replace('%20', ' ')
            current_item.saves_count_datetime = utc_now

            try:
                current_item.image = req.get(image, allow_redirects=True).url
            except req.RequestException:
                current_item.image = None

            if self.parse:
                log.info('Downloading article for {}'.format(item_id))
                article = PocketArticleDownloader(current_item).download()
                current_item.article = article

        for a in soup.find_all('a'):
            if 'related_top' in a.get('href'):
                related_topics_labels.append(a.text)

        scraped_topic = PocketTopic(self._topic_label)
        scraped_topic.items = pocket_items
        scraped_topic.related_topics = [PocketTopic(l) for l in related_topics_labels]

        return scraped_topic


if __name__ == '__main__':
    PocketTopicScraper('python', limit=10, parse=True).scrap().to_dict()
