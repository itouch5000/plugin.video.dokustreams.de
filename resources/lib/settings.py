import xbmcaddon

from resources.lib.logger import Logger


__addon__ = xbmcaddon.Addon('plugin.video.dokustreams.de')

logger = Logger(__name__)


def get_setting(name):
    value = __addon__.getSetting(name)
    logger.debug("get setting {0} = {1} ({2})".format(name, value, type(value)))
    return value


def set_setting(name, value):
    logger.debug("set setting {0} = {1} ({2})".format(name, value, type(value)))
    __addon__.setSetting(name, value)
