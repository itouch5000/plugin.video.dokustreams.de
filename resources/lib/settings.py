import xbmcaddon


__addon__ = xbmcaddon.Addon('plugin.video.dokustreams.de')


def get_setting(name):
    return __addon__.getSetting(name)


def set_setting(name, value):
    __addon__.setSetting(name, value)
