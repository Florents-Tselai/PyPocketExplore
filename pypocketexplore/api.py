#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

__author__ = 'Florents Tselai'

from flask import Flask, jsonify, request

from pypocketexplore.jobs import download_topic_items
from pypocketexplore.parser import PocketTopicScraper
from pypocketexplore import setup_logger

app = Flask(__name__)
app.logger.handlers.extend(setup_logger(__name__).handlers)


@app.route("/api/topic/<topic>", methods=["GET"])
def get_topic(topic):
    try:
        limit = int(request.args.get('limit', None))
    except TypeError:
        limit = None
    label = topic
    run_async = request.args.get('async', 'false') == 'true'
    parse = request.args.get('parse', 'false') == 'true'
    if run_async:
        job = download_topic_items.delay(label, limit, parse)
        return jsonify({'topic': topic, 'job_id': job.get_id()})

    topic_scraped = PocketTopicScraper(topic, limit, parse).scrap()

    return jsonify(topic_scraped.to_dict())


def main():
    app.run('localhost', 5000, debug=True)


if __name__ == '__main__':
    main()
