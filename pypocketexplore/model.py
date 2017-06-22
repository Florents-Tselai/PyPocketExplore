__author__ = 'Florents Tselai'


class PocketItem:
    def __init__(self, item_id):
        self._item_id = item_id

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @property
    def saves_count(self):
        return self._saves_count

    @saves_count.setter
    def saves_count(self, saves_count):
        self._saves_count = saves_count

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @property
    def topic(self):
        return self._topic

    @topic.setter
    def topic(self, topic):
        self._topic = topic

    @property
    def excerpt(self):
        return self._excerpt

    @excerpt.setter
    def excerpt(self, excerpt):
        self._excerpt = excerpt

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image):
        self._image = image

    @property
    def saves_count_datetime(self):
        return self._saves_count_datetime

    @saves_count_datetime.setter
    def saves_count_datetime(self, saves_count_datetime):
        self._saves_count_datetime = saves_count_datetime

    @property
    def article(self):
        return self._article

    @article.setter
    def article(self, article):
        self._article = article

    @property
    def item_id(self):
        return self._item_id

    def to_dict(self):
        return dict((get_key(key), value)
                    for key, value in self.__dict__.items()
                    if not callable(value) and not key.startswith("__"))


class PocketTopic:
    def __init__(self, label):
        self._label = label
        self._items = []
        self._related_topics = []

    @property
    def related_topics(self):
        return self._related_topics

    @related_topics.setter
    def related_topics(self, related_topics):
        self._related_topics = related_topics

    @property
    def label(self):
        return self._label

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, items):
        self._items = items

    def to_dict(self):
        return {
            'label': self._label,
            'items': [item.to_dict() for item in self._items],
            'related_topics': [topic.label for topic in self.related_topics]
        }

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)


def to_dict(model):
    return dict((get_key(key), value)
                for key, value in model.__dict__.items()
                if not callable(value) and not key.startswith("__"))


def get_key(key):
    return key.replace("_", "", 1) if key.startswith("_") else key