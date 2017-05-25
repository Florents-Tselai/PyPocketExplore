#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

__author__ = 'Florents Tselai'

from pprint import pprint

import requests as req
from bs4 import BeautifulSoup
from datetime import datetime
from newspaper import Article, ArticleException

from pypocketexplore.model import PocketItem, PocketTopic

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
    def __init__(self, topic,
                 limit=None,
                 collection=None,
                 parse=False):
        if isinstance(topic, str):
            self._topic = PocketTopic(topic)
        elif isinstance(topic, PocketTopic):
            self._topic = topic
        else:
            raise TypeError

        self.limit = limit
        self.collection = collection
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
        for data_id, title, excerpt, saves_count, image in zip(data_ids[1::2], titles, excerpts, saves_counts, images):
            if self.limit and len(self.topic.items) == self.limit:
                break
            item = PocketItem(data_id)
            item.url = soup.find('a', attrs={'data-id': data_id}).get('data-saveurl')
            item.title = title
            item.excerpt = excerpt
            item.saves_count = saves_count
            item.topic = self.topic.label.replace('%20', ' ')
            item.saves_count_datetime = utc_now
            self._topic.items.append(item)

            try:
                item.image = req.get(image, allow_redirects=True).url
            except Exception:
                item.image = None

            if self.parse:
                PocketItemDownloader(item)

            print("Saving item {} from topic {}".format(item.title, self.topic.label))
            self.collection.update({'item_id': item.item_id},
                                   item.to_dict(), upsert=True)

        for a in soup.find_all('a'):
            if 'related_top' in a.get('href'):
                self._topic.related_topics.append(PocketTopic(a.text))