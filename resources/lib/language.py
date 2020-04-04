import xbmcaddon


__addon__ = xbmcaddon.Addon('plugin.video.dokustreams.de')


class Language(object):
    general = __addon__.getLocalizedString(32000)
    per_page = __addon__.getLocalizedString(32001)
    next_page = __addon__.getLocalizedString(32002)
    show_tags = __addon__.getLocalizedString(32004)
    show_categories = __addon__.getLocalizedString(30005)
    documentations = __addon__.getLocalizedString(30006)
    tags = __addon__.getLocalizedString(30007)
    categories = __addon__.getLocalizedString(30008)
    playlist = __addon__.getLocalizedString(30009)
    video = __addon__.getLocalizedString(30010)
    search = __addon__.getLocalizedString(30011)
    select_mirror_for = __addon__.getLocalizedString(30013)
    search_documentations = __addon__.getLocalizedString(30014)
    error = __addon__.getLocalizedString(30016)
    search_tags = __addon__.getLocalizedString(30018)
    search_categories = __addon__.getLocalizedString(30019)
    short_documentations = __addon__.getLocalizedString(30020)
