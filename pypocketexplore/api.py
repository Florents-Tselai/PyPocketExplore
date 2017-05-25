#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

__author__ = 'Florents Tselai'

from flask import Flask, jsonify, request
from pymongo import MongoClient
from redis import StrictRedis
from rq import Queue

from pypocketexplore.config import MONGO_URI
from pypocketexplore.jobs import download_topic_items
from pypocketexplore.model import PocketTopic
from pypocketexplore.parser import PocketTopicScraper

app = Flask(__name__)

db = MongoClient(MONGO_URI).get_default_database()
redis = StrictRedis()

ITEMS_COLLECTION = db.get_collection('pocket.items')
TOPICS_COLLECTION = db.get_collection('pocket.topics')
ITEMS_QUEUE = Queue('pocket.items', connection=StrictRedis())
TOPICS_QUEUE = Queue('pocket.topics', connection=StrictRedis())


@app.route("/api/topic/<topic>", methods=["GET"])
def get_topic(topic):
    limit = request.args.get('limit', None)
    label = topic
    run_async = request.args.get('async', 'false') == 'true'
    if run_async:
        job = download_topic_items.delay(label)
        return jsonify({'topic': topic, 'job_id': job.get_id()})

    parse = request.args.get('parse', 'false') == 'true'

    topic = PocketTopic(label)
    PocketTopicScraper(topic, limit, ITEMS_COLLECTION, parse)

    return jsonify(topic.to_dict())


def main():
    app.run('localhost', 5000, debug=True)


if __name__ == '__main__':
    main()
