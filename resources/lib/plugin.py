import sys
import types

try:
    # python 3
    from urllib.parse import urlencode, parse_qs, unquote_plus, urlparse
except ImportError:
    # python 2
    from urlparse import parse_qs, urlparse
    from urllib import urlencode, unquote_plus

from resources.lib.logger import Logger


addon_id = "plugin.video.dokustreams.de"

logger = Logger(__name__)
handle = int(sys.argv[1])
actions = {}


def get_params(url):
    query_string = urlparse(url).query
    params_multiple = parse_qs(query_string)
    params = {}
    for key, values in params_multiple.items():
        value = values[0]
        value = unquote_plus(value)
        params[key] = value
    return params


def get_url(**params):
    # translate action functions to their names
    action_key = "action"
    action_val = params.get(action_key)
    if isinstance(action_val, types.FunctionType):
        params[action_key] = action_val.__name__
    # encode params
    query_string = urlencode(params)
    # build plugin url
    url = "plugin://{id}/?{qs}".format(id=addon_id, qs=query_string)
    return url


def action():
    def wrap(func):
        name = func.__name__
        if name not in actions:
            actions[name] = func
            return func
    return wrap


def run():
    url = sys.argv[2]
    logger.debug("url: {0}".format(url))
    params = get_params(url)
    logger.debug("params: {0}".format(params))
    action_val = params.get('action')
    logger.debug("action: {0}".format(action_val))

    if action_val:
        actions[action_val](params)
    else:
        actions["root"](params)
