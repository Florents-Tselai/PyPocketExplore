#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import requests as req
from bs4 import BeautifulSoup
from redis import StrictRedis
from rq import Queue
from tqdm import tqdm
from pypocketexplore.jobs import extract_topic_items
from pymongo import MongoClient
from pypocketexplore.config import MONGO_URI

def main():
    html = req.get("https://www.ibm.com/watson/developercloud/doc/natural-language-understanding/categories.html").content
    soup = BeautifulSoup(html, 'html.parser')
    topics = set()
    for td in soup.find_all('td'):
        if td.text != '':
            topics.add(td.text)
    print("Finished! Fetched {} topics labels".format(len(topics)))
    q = Queue('topics', connection=StrictRedis(), timeout=10 * 60)
    for topic in tqdm(topics):
        q.enqueue_call(extract_topic_items, kwargs=dict(topic=topic))


if __name__ == '__main__':
    main()
