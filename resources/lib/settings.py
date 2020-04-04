import xbmcaddon

from resources.lib.logger import Logger


__addon__ = xbmcaddon.Addon()

logger = Logger(__name__)


def get_setting(name, typ=str):
    value = __addon__.getSetting(name)
    value = typ(value)
    logger.debug("get setting {0} = {1}".format(name, value))
    return value


def set_setting(name, value):
    value = str(value)
    logger.debug("set setting {0} = {1}".format(name, value))
    __addon__.setSetting(name, value)
