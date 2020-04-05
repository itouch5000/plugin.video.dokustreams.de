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
actions = {}
is_python2 = sys.version_info.major == 2


class Logger(object):
    def __init__(self, name=None):
        self.name = name

    def _log(self, msg, level):
        if self.name:
            msg = "{0}: {1}".format(self.name, msg)
        xbmc.log(msg, level)

    def debug(self, msg):
        """
        In depth information about the status of Kodi. This information can pretty much only be deciphered by a developer or long time Kodi power user.

        :param msg: The log message.
        :return:
        """
        self._log(msg, xbmc.LOGDEBUG)

    def info(self, msg):
        """
        Something has happened. It's not a problem, we just thought you might want to know. Fairly excessive output that most people won't care about.

        :param msg: The log message.
        :return:
        """
        self._log(msg, xbmc.LOGINFO)

    def notice(self, msg):
        """
        Similar to INFO but the average Joe might want to know about these events. This level and above are logged by default.

        :param msg: The log message.
        :return:
        """
        self._log(msg, xbmc.LOGNOTICE)

    def warning(self, msg):
        """
        Something potentially bad has happened. If Kodi did something you didn't expect, this is probably why. Watch for errors to follow.

        :param msg: The log message.
        :return:
        """
        self._log(msg, xbmc.LOGWARNING)

    def error(self, msg):
        """
        This event is bad. Something has failed. You likely noticed problems with the application be it skin artifacts, failure of playback a crash, etc.

        :param msg: The log message.
        :return:
        """
        self._log(msg, xbmc.LOGERROR)

    def fatal(self, msg):
        """
        We're screwed. Kodi is about to crash.

        :param msg: The log message.
        :return:
        """
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
    return __addon__.getLocalizedString(string_id)


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
