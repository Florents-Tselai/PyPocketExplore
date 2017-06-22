from flask import Flask, jsonify, request

from pypocketexplore import setup_logger
from pypocketexplore.parser import PocketTopicScraper

app = Flask(__name__)
app.logger.handlers.extend(setup_logger(__name__).handlers)


@app.route("/api/topic/<label>", methods=["GET"])
def get_topic(label):
    try:
        limit = int(request.args.get('limit', None))
    except TypeError:
        limit = None
    parse = request.args.get('parse', 'false') == 'true'

    topic_scraped = PocketTopicScraper(label, limit, parse).scrap()

    return jsonify(topic_scraped.to_dict())


def main():
    app.run('localhost', 5000, debug=True)


if __name__ == '__main__':
    main()
