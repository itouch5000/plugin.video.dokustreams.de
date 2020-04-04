import sys

try:
    # python 3
    from urllib.parse import urlencode
except ImportError:
    # python 2
    from urllib import urlencode


addon_id = "plugin.video.dokustreams.de"
handle = int(sys.argv[1])


def get_url(**params):
    query_string = urlencode(params)
    url = "plugin://{id}/?{qs}".format(id=addon_id, qs=query_string)
    return url
