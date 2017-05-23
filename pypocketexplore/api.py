#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

__author__ = 'Florents Tselai'

from flask import Flask, jsonify, request

from pypocketexplore.parser import PocketTopicScraper
from pprint import pprint
from pypocketexplore.config import MONGO_URI
from redis import StrictRedis
from pymongo import MongoClient
from rq import Queue
from pypocketexplore.jobs import extract_topic_items

app = Flask(__name__)


@app.route("/api/topic/<topic>", methods=["GET"])
def get_topic(topic):

    if request.args.get('async', 'false') == 'true':
        db = MongoClient(MONGO_URI).get_default_database()
        q = Queue('topics', connection=StrictRedis())
        job = q.enqueue_call(extract_topic_items, kwargs=dict(topic=topic), timeout=10 * 60)
        return jsonify({
            'topic': topic,
            'job': job.get_id()
        })


    results = PocketTopicScraper(topic).scrap()
    #pprint(results)

    return jsonify(results)

def main():
    app.run('localhost', 5000, debug=True)

if __name__ == '__main__':
    main()