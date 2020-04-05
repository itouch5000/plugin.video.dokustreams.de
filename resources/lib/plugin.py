import sys
import types

try:
    # python 3
    from urllib.parse import urlencode
except ImportError:
    # python 2
    from urllib import urlencode


addon_id = "plugin.video.dokustreams.de"
handle = int(sys.argv[1])


def get_url(**params):
    # translate action functions to their names
    action_key = "action"
    action = params.get(action_key)
    if isinstance(action, types.FunctionType):
        params[action_key] = action.__name__
    # encode params
    query_string = urlencode(params)
    # build plugin url
    url = "plugin://{id}/?{qs}".format(id=addon_id, qs=query_string)
    return url
