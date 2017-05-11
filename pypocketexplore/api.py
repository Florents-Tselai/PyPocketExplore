#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

__author__ = 'Florents Tselai'

from flask import Flask, jsonify

from pypocketexplore.parser import PocketTopicScraper

app = Flask(__name__)


@app.route("/api/topic/<topic>", methods=["GET"])
def get_topic(topic):
    items = list(PocketTopicScraper(topic).scrap())
    return jsonify(items)