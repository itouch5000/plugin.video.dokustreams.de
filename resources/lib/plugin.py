import sys
try:
    import urllib.parse as urllib
except ModuleNotFoundError:
    import urllib


addon_id = "plugin.video.dokustreams.de"
handle = int(sys.argv[1])


def get_url(**params):
    query_string = urllib.urlencode(params)
    url = "plugin://{id}/?{qs}".format(id=addon_id, qs=query_string)
    return url
