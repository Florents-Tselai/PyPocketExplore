#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

__author__ = 'Florents Tselai'

from urllib.request import urlopen, Request

from bs4 import BeautifulSoup
from datetime import datetime
import requests as req
from newspaper import Article, ArticleException
import json
from newspaper import news_pool
from pprint import pprint
from pypocketexplore.model import PocketItem, to_dict


class ArticleDownloader(Article):
    def __init__(self, args, **kwargs):
        super().__init__(args, **kwargs)

    def download(self):
        super().download()
        self.parse()
        self.nlp()

        self.tags = list(self.tags)

        if self.publish_date:
            self.publish_date = self.publish_date.timestamp()

        self.images = list(self.images)
        self.imgs = list(self.imgs)


class PocketTopicScraper:
    def __init__(self, topic):
        self.topic = topic

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
        items = []
        for data_id, title, excerpt, saves_count, image in zip(data_ids[1::2], titles, excerpts, saves_counts, images):
            item = PocketItem(data_id)
            item.url = soup.find('a', attrs={'data-id': data_id}).get('data-saveurl')
            item.title = title
            item.excerpt = excerpt
            item.saves_count = saves_count
            item.topic = self.topic.replace('%20', ' ')
            item.saves_count_datetime = utc_now
            items.append(item)

            try:
                item.image = req.get(image, allow_redirects=True).url
            except Exception:
                item.image = None

            article_attributes = [
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
            try:
                article = ArticleDownloader(item.url)
                article.download()
                item.article = dict((k, v) for k, v in article.__dict__.items() if k in article_attributes)
                print(to_dict(item))
            except ArticleException:
                item.article = None

        related_topics = []
        for a in soup.find_all('a'):
            if 'related_top' in a.get('href'):
                related_topics.append(a.text)

        return {
            'items': list(map(to_dict, items)),
            'related_topics': related_topics,
            'count': len(items)
        }


if __name__ == '__main__':
    # Download Article
    #a = ArticleDownloader('https://www.nytimes.com/2016/01/10/opinion/sunday/you-dont-need-more-free-time.html')
    #a.download()
    #from json import dumps

    #print(dumps(dict((k, v) for k, v in a.__dict__.items() if k in article_attributes), indent=4))
    res = PocketTopicScraper('finance').scrap()
    from pprint import pprint
    pprint(res)
