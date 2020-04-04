import sys
try:
    # python 3
    import urllib.parse as urllib
except ModuleNotFoundError:
    # python 2
    import urllib

from resources.lib import dokustreams


def get_params(url):
    query_string = urllib.urlparse(url).query
    params_multiple = urllib.parse_qs(query_string)
    params = {}
    for key, values in params_multiple.items():
        value = values[0]
        value = urllib.unquote_plus(value)
        params[key] = value
    return params


def run():
    url = sys.argv[2]
    params = get_params(url)
    action = params.get('action', '')

    if action == "all_posts":
        dokustreams.all_posts(params)
    if action == "multiple_videos_playlists":
        dokustreams.multiple_videos_playlists(params)
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
