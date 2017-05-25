#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

__author__ = 'Florents Tselai'

from flask import Flask, jsonify, request
from pymongo import MongoClient

from pypocketexplore import config
from pypocketexplore.jobs import download_topic_items
from pypocketexplore.model import PocketTopic
from pypocketexplore.parser import PocketTopicScraper

app = Flask(__name__)


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

    db = Mon
    topic = PocketTopic(label)
    PocketTopicScraper(topic, limit, items_collection, parse)

    return jsonify(topic.to_dict())


def main():
    app.run('localhost', 5000, debug=True)


if __name__ == '__main__':
    main()
