# [`PyPocketExplore`](http://tselai.com/pypocketexplore-collecting-exploring-predicting-pocket-items-machine-learning.html) - Unofficial API to [Pocket Explore](https://getpocket.com/explore/) data

[`PyPocketExplore`](http://tselai.com/pypocketexplore-collecting-exploring-predicting-pocket-items-machine-learning.html) 
is a CLI-based and web-based API to access [Pocket Explore](https://getpocket.com/explore/) data.
It can be used to collect data about the most popular Pocket items for different topics.

An example usage would be crawling the data and use it as a training set to predict the number of pocket saves for a web page.

## Usage

The easiest way to install the package is through PyPi.
This should get you up-and-running pretty quickly.
```shell
$ pip install PyPocketExplore
```

Through the CLI there are two modes: `topic` and `batch`

With the first one (`pypocketexplore topic`) you can download items from specific topics and output them to a nicely formatted JSON file.

```bash
Usage: pypocketexplore topic [OPTIONS] [LABEL]...

  Download items for specific topics

Options:
  --limit INTEGER  Limit items to download
  --out TEXT       JSON output filepath
  --nlp            If set, also downloads the page and applies NLP (through
                   NLTK)
```

For example, this command
```bash
$ pypocketexplore topic python data sex books --nlp --out life_topics.json
```
will go through the corresponding pages: 
`https://getpocket.com/explore/python, https://getpocket.com/explore/data, https://getpocket.com/explore/sex, https://getpocket.com/explore/books`
one-by-one and then:

* scrap and extract the immediately available data for each item (`item_id, title, save count, excerpt and url`)
* run each item url through the awesome [Newspaper](http://newspaper.readthedocs.io/en/latest/) library (in-parallel)
* apply NLP to each item's text
* save the results to `life_topics.json`

In the end you'll have a **rich dataset full of text to play with and of course a popularity metric** - pretty cool to experiment with.
You can check it out [here](https://tselai.com/data/life_topics.json)

For each topic on *Pocket Explore*, there are a set of `related topics` which one can crawl through pretty easily
in a recursive way.
For example after scraping `https://getpocket.com/explore/python` on can then scrap the 
`related topics: programming javascript google windows java linux data science python 3 developer`.

This essentially means that one can crawl through the whole graph of topics by following the `related topics` as edges. 
To do this one of course needs a set of *seed topics* to initiate the crawling process.
To get these seeds, the `pypocketexplore batch` mode fetches the taxonomy labels provided by [IBM Watson](https://www.ibm.com/watson/developercloud/doc/natural-language-understanding/categories.html).
and then walks through the graph.
(I guess Pocket uses the IBM Watson to label its items, so this kind of reverse-engineering make sense. (Sorry Pocket guys) )

```bash
Usage: pypocketexplore batch [OPTIONS]

  Download items for all topics recursively.  USE WITH CAUTION!

Options:
  --n INTEGER      Max number of total items to download
  --limit INTEGER  Limit items to download per topic
  --out TEXT       JSON output filepath
  --nlp            If set, also downloads the page and applies NLP (through
                   NLTK)
  --mongo TEXT     Mongo DB URI to save items
  --help           Show this message and exit.
```

**CAUTION**
This mode with all goodies enabled will take few days to run and then collect around 300k unique items
through 8k topics.
I have tried to space the requests to Pocket's servers and handle rate limit errors, 
but one can never be sure with such things.

## Web API

To have access to a standalone web API you need to clone the repo locally first.
```shell
$ git clone git@github.com:Florents-Tselai/PyPocketExplore.git
$ cd PyPocketExplore
$ pip install -r requirements.txt
```

To run this API application, use the `flask` command as same as [Flask Quickstart](http://flask.pocoo.org/docs/0.12/quickstart/)

```shell
$ cd PyPocketExplore
$ export FLASK_APP=./PyPocketExplore/pypocketexplore/api/api.py
$ export FLASK_DEBUG=1 ## if you run in debug mode.
$ flask run
 * Running on http://localhost:5000/
```

## Web API Documentation

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
