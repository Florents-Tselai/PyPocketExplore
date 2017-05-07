# PyPocketExplore - Unofficial API to [Pocket Explore](https://getpocket.com/explore/) data

This is a flask-based API to access [Pocket Explore](https://getpocket.com/explore/)
It can be used to collect data about the most popular Pocket items in different topics.

An example usage would be crawling the data and use it as a training set to predict the number of pocket saves for a web page

## Installation
Before running *PyPocketExplore API*, you have to clone the code from this repository, install requirements at first.

```shell
$ git clone git@github.com:Florents-Tselai/PyPocketExplore.git
$ cd PyPocketExplore
$ pip install -r requirements.txt
```

## Usage
To run this API application, use the `flask` command as same as [Flask Quickstart](http://flask.pocoo.org/docs/0.12/quickstart/)

```shell
$ export FLASK_APP=./PyPocketExplore/api/api.py
$ export FLASK_DEBUG=1 ## if you run in debug mode.
$ flask run
 * Running on http://localhost:5000/
```

## Documentation

### Topic
* `GET /api/topic/{topic}` - Get topic data

Example topics: `python, finance, business` and more

Example `GET /api/topic/python`

#### Response
```json
[
    {
        "excerpt": "For part 1, see here. All the software written for this project is in Python. I’m not an expert python programmer, far from it but the huge number of available libraries and the fact that I can make some sense of it all without having spent a lifetime in Python made this a fairly obvious choice.",
        "image": "https://d33ypg4xwx0n86.cloudfront.net/direct?"url"=https%3A%2F%2Fjacquesmattheij.com%2Fusb-microscope.jpg&resize=w750",
        "item_id": "1731527024",
        "saves_count": 223,
        "title": "Sorting 2 Tons of Lego, The software Side · Jacques Mattheij",
        "topic": "python",
        "url": "https://jacquesmattheij.com/sorting-lego-the-software-side"
    },
    
        {
        "excerpt": "There are lots of free resources for learning Python available now. I wrote about some of them way back in 2013, but there’s even more now then there was then! In this article, I want to share these resources with you.",
        "image": "https://d33ypg4xwx0n86.cloudfront.net/direct?"url"=https%3A%2F%2Fdz2cdn1.dzone.com%2Fstorage%2Farticle-thumb%2F5158392-thumb.jpg&resize=w750",
        "item_id": "1727350036",
        "saves_count": 59,
        "title": "Free Python Resources",
        "topic": "python",
        "url": "https://dzone.com/articles/free-python-resources"
    },
    
    {
        "excerpt": "A surprisingly versatile Swiss Army knife — with very long blades!TL;DRWe (an investment bank in the Eurozone) are deploying Jupyter and the Python scientific stack in a corporate environment to provide employees and contractors with an interactive computing environment with to help them leve",
        "image": "https://d33ypg4xwx0n86.cloudfront.net/direct?"url"=https%3A%2F%2Fcdn-"image"s-1.medium.com%2Fmax%2F1600%2F1%2AmeN9gfB_nuwmGGwLQzhVQA.png&resize=w750",
        "item_id": "1726489646",
        "saves_count": 41,
        "title": "Jupyter & Python in the corporate LAN",
        "topic": "python",
        "url": "https://medium.com/@olivier.borderies/jupyter-python-in-the-corporate-lan-109e2ffde897"
    },
    ...
]
```


License
-------

Copyright (c) 2017 [Florents Tselai](https://tselai.com)
Licensed under the [MIT license](http://opensource.org/licenses/MIT).
