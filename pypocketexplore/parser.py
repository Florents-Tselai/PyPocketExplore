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

from pypocketexplore.model import PocketItem, PocketTopic
from pypocketexplore.config import MONGO_URI, ITEMS_COLLECTION_NAME

print = pprint


class PocketItemDownloader:
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

        try:
            article = Article(self._pocket_item.url)
            article.download()
            article.parse()
            article.nlp()

            article.tags = list(article.tags)
            if article.publish_date:
                article.publish_date = article.publish_date.timestamp()

            article.images = list(article.images)

            self._pocket_item.article = dict((k, v)
                                             for k, v in article.__dict__.items()
                                             if k in self.ARTICLE_ATTRIBUTES_TO_KEEP
                                             )
        except ArticleException:
            self._pocket_item.article = {}


class PocketTopicScraper:
    def __init__(self, topic_label,
                 limit=None,
                 parse=False):
        if isinstance(topic_label, str):
            self._topic = PocketTopic(topic_label)
        else:
            raise TypeError('Can only pass str')

        self.limit = limit
        self.parse = parse

        self.scrap()

    @property
    def topic(self):
        return self._topic

    def _make_request(self, topic):
        html = req.get("http://getpocket.com/explore/{}".format(topic), headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }).content

        return html

    def scrap(self):
        html = self._make_request(self.topic)
        utc_now = datetime.utcnow().timestamp()
        soup = BeautifulSoup(html, 'html.parser')
        data_ids = [a.get('data-id') for a in soup.find_all('a', class_='link_track')]
        titles = [a.text for a in soup.find_all('a', class_='link_track') if a.text != '\n \n']
        excerpts = [p.text for p in soup.find_all('p', class_='excerpt')]
        saves_counts = [int(a.text.replace(' saves', '').replace(',', '')) for a in
                        soup.find_all('div', class_='save_count')]
        images = [div.get('data-thumburl') for div in soup.find_all('div', class_='item_image')]

        for item_id, title, excerpt, saves_count, image in tqdm(zip(data_ids[1::2], titles, excerpts, saves_counts, images)):
            if self.limit and len(self.topic.items) >= self.limit:
                break
            print('Downloading item {}'.format(item_id))
            current_item = PocketItem(item_id)

            current_item.url = soup.find('a', attrs={'data-id': item_id}).get('data-saveurl')
            current_item.title = title
            current_item.excerpt = excerpt
            current_item.saves_count = saves_count
            current_item.topic = self.topic.label.replace('%20', ' ')
            current_item.saves_count_datetime = utc_now

            try:
                current_item.image = req.get(image, allow_redirects=True).url
            except req.RequestException:
                current_item.image = None

            if self.parse:
                PocketItemDownloader(current_item)

            self._topic.items.append(current_item)

        for a in soup.find_all('a'):
            if 'related_top' in a.get('href'):
                self._topic.related_topics.append(PocketTopic(a.text))

        return self.topic