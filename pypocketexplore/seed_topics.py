#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import requests as req
from bs4 import BeautifulSoup
from redis import StrictRedis
from rq import Queue
from tqdm import tqdm


def main():
    html = req.get(
        "https://www.ibm.com/watson/developercloud/doc/natural-language-understanding/categories.html").content
    soup = BeautifulSoup(html, 'html.parser')
    topics = set()
    for td in soup.find_all('td'):
        if td.text != '':
            topics.add(td.text)

    for topic in topics:
        resp = req.get('http://localhost:5000/api/topic/{}?async=true&parse=true'.format(topic))
        print(resp.json())

    print("Finished! Fetched {} topics labels".format(len(topics)))

if __name__ == '__main__':
    main()
