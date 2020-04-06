import sys
import types

try:
    # python 3
    from urllib.parse import urlencode, parse_qs, unquote_plus, urlparse
except ImportError:
    # python 2
    from urlparse import parse_qs, urlparse
    from urllib import urlencode, unquote_plus

import xbmc
import xbmcaddon


__addon__ = xbmcaddon.Addon()
addon_id = __addon__.getAddonInfo("id")
handle = int(sys.argv[1])
is_python2 = sys.version_info.major == 2
actions = {}


class Logger(object):
    def __init__(self, name=None):
        self.name = name

    def _log(self, msg, level):
        if self.name:
            msg = "{0}: {1}".format(self.name, msg)
        xbmc.log(msg, level)

    def debug(self, msg):
        self._log(msg, xbmc.LOGDEBUG)

    def info(self, msg):
        self._log(msg, xbmc.LOGINFO)

    def notice(self, msg):
        self._log(msg, xbmc.LOGNOTICE)

    def warning(self, msg):
        self._log(msg, xbmc.LOGWARNING)

    def error(self, msg):
        self._log(msg, xbmc.LOGERROR)

    def fatal(self, msg):
        self._log(msg, xbmc.LOGFATAL)


logger = Logger(__name__)


def py2_decode(value):
    if is_python2:
        return value.decode('utf-8')
    return value


def py2_encode(value):
    if is_python2:
        return value.encode('utf-8')
    return value


def get_string(string_id):
    value = __addon__.getLocalizedString(string_id)
    value = py2_encode(value)
    return value


def get_setting(name, typ=str):
    value = __addon__.getSetting(name)
    value = typ(value)
    logger.debug("get setting {0} = {1}".format(name, value))
    return value


def set_setting(name, value):
    value = str(value)
    logger.debug("set setting {0} = {1}".format(name, value))
    __addon__.setSetting(name, value)


def get_params(url):
    query_string = urlparse(url).query
    params_multiple = parse_qs(query_string)
    params = {}
    for key, values in params_multiple.items():
        value = values[0]
        value = unquote_plus(value)
        params[key] = value
    return params


def build_query_string(params):
    # encode values if necessary
    for key, value in params.items():
        try:
            key = py2_encode(key)
        except (AttributeError, UnicodeDecodeError, UnicodeEncodeError):
            pass
        try:
            value = py2_encode(value)
            params[key] = value
        except (AttributeError, UnicodeDecodeError, UnicodeEncodeError):
            pass
    # url encode params
    query_string = urlencode(params)
    return query_string


def get_url(**params):
    # translate action functions to their names
    action_key = "action"
    action_val = params.get(action_key)
    if isinstance(action_val, types.FunctionType):
        params[action_key] = action_val.__name__
    query_string = build_query_string(params)
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
