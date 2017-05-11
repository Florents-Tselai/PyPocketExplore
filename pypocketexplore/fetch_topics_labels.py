#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import requests as req
from bs4 import BeautifulSoup
from tqdm import tqdm
from time import sleep
from random import choice
import 


def main():
    html = req.get("https://www.ibm.com/watson/developercloud/doc/natural-language-understanding/categories.html").content
    soup = BeautifulSoup(html, 'html.parser')
    topics = set()
    for td in soup.find_all('td'):
        if td.text != '':
            topics.add(td.text)
    print("Finished! Fetched {} topics labels".format(len(topics)))
    for topic in tqdm(topics):
        print(topic)
        sleep(choice(range(5, 10)))


if __name__ == '__main__':
    main()