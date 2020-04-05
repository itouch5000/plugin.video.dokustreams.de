import sys

try:
    # python 3
    from urllib.parse import parse_qs, unquote_plus, urlparse
except ImportError:
    # python 2
    from urlparse import parse_qs, urlparse
    from urllib import unquote_plus

from resources.lib import dokustreams
from resources.lib.logger import Logger


logger = Logger(__name__)


def get_params(url):
    query_string = urlparse(url).query
    params_multiple = parse_qs(query_string)
    params = {}
    for key, values in params_multiple.items():
        value = values[0]
        value = unquote_plus(value)
        params[key] = value
    return params


def run():
    url = sys.argv[2]
    logger.debug("url: {0}".format(url))
    params = get_params(url)
    logger.debug("params: {0}".format(params))
    action = params.get('action')
    logger.debug("action: {0}".format(action))

    if action == "all_posts":
        dokustreams.all_posts(params)
    if action == "all_tags":
        dokustreams.all_tags(params)
    if action == "all_categories":
        dokustreams.all_categories(params)
    if action == "search_posts":
        dokustreams.search_posts(params)
    if action == "search_tags":
        dokustreams.search_tags(params)
    if action == "search_categories":
        dokustreams.search_categories(params)
    if action == "posts_by_url":
        dokustreams.posts_by_url(params)
    if action == "tags_by_url":
        dokustreams.tags_by_url(params)
    if action == "categories_by_url":
        dokustreams.categories_by_url(params)
    if action == "posts_by_tag":
        dokustreams.posts_by_tag(params)
    if action == "posts_by_category":
        dokustreams.posts_by_category(params)
    if action == "tags_by_post":
        dokustreams.tags_by_post(params)
    if action == "categories_by_post":
        dokustreams.categories_by_post(params)
    if action == "play":
        dokustreams.play(params)
    else:
        dokustreams.root(params)
