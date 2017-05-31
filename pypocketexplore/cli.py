__author__ = 'Florents Tselai'

import json
from logging import ERROR

import click

from pypocketexplore.parser import PocketTopicScraper, logger

logger.setLevel(ERROR)


@click.command('topic')
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


def main():
    topic()


if __name__ == '__main__':
    main()
