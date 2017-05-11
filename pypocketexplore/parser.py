#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

__author__ = 'Florents Tselai'

from urllib.request import urlopen, Request

from bs4 import BeautifulSoup

from pypocketexplore.model import PocketItem, to_dict


class PocketTopicScraper:
    def __init__(self, topic):
        self.topic = topic

    def _make_request(self, topic):
        req = Request(
            "http://getpocket.com/explore/%s" % topic.replace(' ', '%20'),
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )
        return urlopen(req).read().decode('utf-8')

    def scrap(self):
        html = self._make_request(self.topic)
        soup = BeautifulSoup(html, 'lxml')
        data_ids = [a.get('data-id') for a in soup.find_all('a', class_='link_track')]
        titles = [a.text for a in soup.find_all('a', class_='link_track') if a.text != '\n \n']
        excerpts = [p.text for p in soup.find_all('p', class_='excerpt')]
        saves_counts = [int(a.text.replace(' saves', '').replace(',', '')) for a in
                        soup.find_all('div', class_='save_count')]
        images = [div.get('data-thumburl') for div in soup.find_all('div', class_='item_image')]
        for data_id, title, excerpt, saves_count, image in zip(data_ids[1::2], titles, excerpts, saves_counts, images):
            item = PocketItem(data_id)
            item.url = soup.find('a', attrs={'data-id': data_id}).get('data-saveurl')
            item.title = title
            item.excerpt = excerpt
            item.saves_count = saves_count
            item.topic = self.topic.replace('%20', ' ')

            yield to_dict(item)
