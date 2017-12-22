# -*- coding: utf-8 -*-
import re
import bs4
import json
import urllib
import urlparse
import requests
from HTMLParser import HTMLParser
from resources.lib.simpleplugin import Plugin, Addon, ListContext

import xbmc
import xbmcgui


ListContext.cache_to_disk = True
plugin = Plugin()
addon = Addon()
_ = plugin.initialize_gettext()


BASE_URL = 'http://dokustreams.de/wp-json/wp/v2'
PER_PAGE = plugin.get_setting('per_page')


class DialogSelect(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.listing = kwargs.get("listing")
        self.title = kwargs.get("title")
        self.totalitems = 0
        self.result = None

    def autofocus_listitem(self):
        pass

    def close_dialog(self, cancelled=False):
        if cancelled:
            self.result = False
        else:
            self.result = self.list_control.getSelectedItem()
        self.close()

    def onInit(self):
        self.list_control = self.getControl(6)
        self.getControl(3).setVisible(False)
        self.list_control.setEnabled(True)
        self.list_control.setVisible(True)
        self.set_cancel_button()
        self.getControl(5).setVisible(False)
        self.getControl(1).setLabel(self.title)
        self.list_control.addItems(self.listing)
        self.setFocus(self.list_control)
        self.totalitems = len(self.listing)
        self.autofocus_listitem()

    def onAction(self, action):
        if action.getId() in (9, 10, 92, 216, 247, 257, 275, 61467, 61448, ):
            self.close_dialog(True)
        if (action.getId() == 7 or action.getId() == 100) and xbmc.getCondVisibility(
                "Control.HasFocus(3) | Control.HasFocus(6)"):
            self.close_dialog()

    def onClick(self, controlID):
        if controlID == 5:
            self.result = True
            self.close()
        else:
            self.close_dialog(True)

    def set_cancel_button(self):
        try:
            self.getControl(7).setLabel(xbmc.getLocalizedString(222))
            self.getControl(7).setVisible(True)
            self.getControl(7).setEnabled(True)
        except Exception:
            pass


def build_url(path, params=None):
    if not params:
        params = dict()
    params.setdefault('per_page', PER_PAGE)
    url = '{0}/{1}?{2}'.format(BASE_URL, path, urllib.urlencode(params))
    return url


def edit_url(url, new_params):
    parsed = urlparse.urlsplit(url)
    params = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))
    params.update(new_params)
    new_url = '{0}://{1}{2}?{3}'.format(parsed.scheme, parsed.netloc, parsed.path, urllib.urlencode(params))
    return new_url


def page_from_url(url):
    params = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))
    page = int(params.get('page', 1))
    return page


def parse_ids_content(content):
    soup = bs4.BeautifulSoup(content, 'html5lib')
    yt_playlists = []
    yt_videos = []
    match = soup.find_all('div', {'class': 'lyMe'})
    for i in match:
        if 'playlist' in i['class']:
            yt_pid = i['id'][4:]
            yt_pimg = soup.find('div', {'id': 'lyte_{0}'.format(yt_pid)})['data-src']
            yt_vid = re.findall('/([^\"&?\/\ ]{11})/hqdefault\.', yt_pimg)[0]
            yt_playlists.append((yt_pid, yt_vid))  # contains tuple with (id, image_id)
        else:
            yt_vid = i['id'][4:]
            yt_videos.append(yt_vid)  # contains id
    return yt_playlists, yt_videos


def list_videos(url, enable_bookmark=True, ):
    json_data = requests.get(url).json()
    listing = []
    for i in json_data:
        _id = i.get('id')
        title = HTMLParser().unescape(i.get('title')['rendered'])
        if type(title) == unicode:
            title = title.encode('utf-8')
        content = i.get('content')['rendered']
        date = i.get('date')[:10]
        slug = i.get('slug')
        soup = bs4.BeautifulSoup(content, 'html5lib')
        try:
            plot = soup.find('meta', {'itemprop': 'description'})['content']
        except TypeError:
            plot = ""
        yt_playlists, yt_videos = parse_ids_content(content)
        context_menu = []
        if enable_bookmark:
            context_menu.append(
                (_("Add to Bookmarks"),
                 'XBMC.RunPlugin({0})'.format(plugin.get_url(action='add_bookmark', id=_id))),
            )
        context_menu += [
            (_("Show tags"),
             'XBMC.Container.Update({0})'.format(plugin.get_url(action='tags_by_post', id=_id))),
            (_("Show categories"),
             'XBMC.Container.Update({0})'.format(plugin.get_url(action='categories_by_post', id=_id))),
            #(_("Force mirror search"),
             #'XBMC.RunPlugin({0})'.format(plugin.get_url(action='force_mirror', name=title))),
        ]
        if len(yt_videos) == 0 and len(yt_playlists) == 0:  # search for mirror
            image = "http://dokustreams.de/wp-content/uploads/{0}.jpg".format(slug)
            listing.append({
                'label': title,
                'thumb': image,
                'info': {'video': {
                    'title': title,
                    'plot': plot,
                    'aired': date,
                    'year': date[:4],
                }},
                'context_menu': context_menu,
                'is_playable': True,
                'url': plugin.get_url(action='play', name=title),
            })
        elif len(yt_videos) == 1 and len(yt_playlists) == 0:  # video direkt starten
            yt_vid = yt_videos[0]
            image = "https://i.ytimg.com/vi/{0}/hqdefault.jpg".format(yt_vid)
            listing.append({
                'label': title,
                'thumb': image,
                'info': {'video': {
                    'title': title,
                    'plot': plot,
                    'aired': date,
                    'year': date[:4],
                }},
                'context_menu': context_menu,
                'is_playable': True,
                'url': plugin.get_url(action='play', youtube_id=yt_vid, name=title),
            })
        elif len(yt_videos) == 0 and len(yt_playlists) == 1:  # playlist direkt anzeigen
            yt_pid, yt_vid = yt_playlists[0]
            image = "https://i.ytimg.com/vi/{0}/hqdefault.jpg".format(yt_vid)
            listing.append({
                'label': title,
                'thumb': image,
                'info': {'video': {
                    'title': title,
                    'plot': plot,
                    'aired': date,
                    'year': date[:4],
                }},
                'context_menu': context_menu,
                'is_playable': False,
                'url': "plugin://plugin.video.youtube/playlist/{0}/".format(yt_pid),
            })
        else:  # playlist und videos zusammen anzeigen
            image = "http://dokustreams.de/wp-content/uploads/{0}.jpg".format(slug)
            listing.append({
                'label': title,
                'thumb': image,
                'context_menu': context_menu,
                'is_playable': False,
                'url': plugin.get_url(action='multiple_videos_playlists', id=_id, name=title),
            })
    if len(json_data) == PER_PAGE:
        next_page = page_from_url(url) + 1
        next_url = edit_url(url, {'page': next_page})
        listing.append({
            'label': '[COLOR blue]{0}[/COLOR]'.format(_("Next page")),
            'url': plugin.get_url(action='posts_by_url', url=next_url),
        })
    return listing


def list_tags(url):
    json_data = requests.get(url).json()
    listing = []
    for i in json_data:
        name = i.get('name')
        tag_id = i.get('id')
        listing.append({
            'label': name,
            'is_playable': False,
            'url': plugin.get_url(action='posts_by_tag', id=tag_id),
        })
    if len(json_data) == PER_PAGE:
        next_page = page_from_url(url) + 1
        next_url = edit_url(url, {'page': next_page})
        listing.append({
            'label': '[COLOR blue]{0}[/COLOR]'.format(_("Next page")),
            'url': plugin.get_url(action='tags_by_url', url=next_url),
        })
    return listing


def list_categories(url):
    json_data = requests.get(url).json()
    listing = []
    for i in json_data:
        name = i.get('name')
        category_id = i.get('id')
        listing.append({
            'label': name,
            'is_playable': False,
            'url': plugin.get_url(action='posts_by_category', id=category_id),
        })
    if len(json_data) == PER_PAGE:
        next_page = page_from_url(url) + 1
        next_url = edit_url(url, {'page': next_page})
        listing.append({
            'label': '[COLOR blue]{0}[/COLOR]'.format(_("Next page")),
            'url': plugin.get_url(action='categories_by_url', url=next_url),
        })
    return listing


def youtube_search(query):
    FIELDS_BASE = ["dateadded", "file", "lastplayed", "plot", "title", "art", "playcount"]
    FIELDS_FILE = FIELDS_BASE + ["streamdetails", "director", "resume", "runtime"]
    FIELDS_FILES = FIELDS_FILE + [
        "plotoutline", "sorttitle", "cast", "votes", "trailer", "year", "country", "studio",
        "genre", "mpaa", "rating", "tagline", "writer", "originaltitle", "imdbnumber", "premiered", "episode",
        "showtitle",
        "firstaired", "watchedepisodes", "duration", "season"]
    data = {
        "jsonrpc": "2.0",
        "method": "Files.GetDirectory",
        "id": 1,
        "params": {
            "properties": FIELDS_FILES,
            "directory": "plugin://plugin.video.youtube/kodion/search/query/?q={0}".format(query)
        }
    }
    json_response = xbmc.executeJSONRPC(json.dumps(data))
    json_object = json.loads(json_response.decode('utf-8'))
    result = []
    if 'result' in json_object:
        for key, value in json_object['result'].iteritems():
            if not key == "limits" and (isinstance(value, list) or isinstance(value, dict)):
                result = value
    result = [i for i in result if not i["filetype"] == "directory"]
    return result


@plugin.action()
def root(params):
    return [
        {'label': _("Documentations"), 'url': plugin.get_url(action='all_posts')},
        {'label': _("Short documentations"), 'url': plugin.get_url(action='multiple_videos_playlists', id=15092, name='Kurzdokus und Reportagen')},
        {'label': _("Tags"), 'url': plugin.get_url(action='all_tags')},
        {'label': _("Categories"), 'url': plugin.get_url(action='all_categories')},
        {'label': _("Search documentations"), 'url': plugin.get_url(action='search_posts')},
        {'label': _("Search tags"), 'url': plugin.get_url(action='search_tags')},
        {'label': _("Search categories"), 'url': plugin.get_url(action='search_categories')},
        {'label': _("Bookmarks"), 'url': plugin.get_url(action='bookmarks')},
    ]


@plugin.action()
def posts_by_url(params):
    url = params.url
    return list_videos(url)


@plugin.action()
def tags_by_url(params):
    url = params.url
    return list_tags(url)


@plugin.action()
def categories_by_url(params):
    url = params.url
    return list_categories(url)


@plugin.action()
def all_posts(params):
    url = build_url('posts')
    return list_videos(url)


@plugin.action()
def all_tags(params):
    url = build_url('tags')
    return list_tags(url)


@plugin.action()
def all_categories(params):
    url = build_url('categories')
    return list_categories(url)


@plugin.action()
def search_posts(params):
    dialog = xbmcgui.Dialog()
    query = dialog.input(_("Search documentations"))
    if query:
        url = build_url('posts', {'search': query})
        return list_videos(url)


@plugin.action()
def search_tags(params):
    dialog = xbmcgui.Dialog()
    query = dialog.input(_("Search tags"))
    if query:
        url = build_url('tags', {'search': query})
        return list_tags(url)


@plugin.action()
def search_categories(params):
    dialog = xbmcgui.Dialog()
    query = dialog.input(_("Search categories"))
    if query:
        url = build_url('categories', {'search': query})
        return list_categories(url)


@plugin.action()
def posts_by_tag(params):
    _id = params.get('id')
    url = build_url('posts', {'tags': _id})
    return list_videos(url)


@plugin.action()
def posts_by_category(params):
    _id = params.get('id')
    url = build_url('posts', {'categories': _id})
    return list_videos(url)


@plugin.action()
def tags_by_post(params):
    post_id = params.id
    url = build_url('tags', {'post': post_id})
    return list_tags(url)


@plugin.action()
def categories_by_post(params):
    post_id = params.id
    url = build_url('categories', {'post': post_id})
    return list_categories(url)


@plugin.action()
def multiple_videos_playlists(params):
    _id = params.id
    title = HTMLParser().unescape(params.name)
    if type(title) == unicode:
        title = title.encode('utf-8')
    url = build_url('posts', {'include': _id})
    i = requests.get(url).json()[0]
    content = i.get('content')['rendered']
    yt_playlists, yt_videos = parse_ids_content(content)
    listing = []
    for index, playlist in enumerate(yt_playlists):
        yt_pid, yt_vid = playlist
        image = "https://i.ytimg.com/vi/{0}/hqdefault.jpg".format(yt_vid)
        listing.append({
            'label': "{0} {1}".format(_("Playlist"), index+1),
            'thumb': image,
            'is_playable': False,
            'url': "plugin://plugin.video.youtube/playlist/{0}/".format(yt_pid),
        })
    for index, yt_vid in enumerate(yt_videos):
        image = "https://i.ytimg.com/vi/{0}/hqdefault.jpg".format(yt_vid)
        listing.append({
            'label': "{0} {1}".format(_("Video"), index+1),
            'thumb': image,
            'is_playable': True,
            'url': plugin.get_url(action='play', youtube_id=yt_vid, name=title),
        })
    return listing


@plugin.action()
def bookmarks(params):
    with plugin.get_storage() as storage:
        if not 'bookmarks' in storage:
            storage['bookmarks'] = []
        ids = storage['bookmarks']
    if not ids:
        return list()
    ids = ','.join(ids)
    url = build_url('posts', {'include': ids})
    listing = list_videos(url, enable_bookmark=False)
    for index, item in enumerate(listing):  # add remove from bookmarks to first position
        old_context = item['context_menu'] if 'context_menu' in item else list()
        item['context_menu'] = list()
        item['context_menu'].append(
            (_("Remove from Bookmarks"),
             'XBMC.RunPlugin({0})'.format(plugin.get_url(action='remove_bookmark', index=index))),
        )
        item['context_menu'] += old_context
    return listing


@plugin.action()
def add_bookmark(params):
    _id = params.id
    with plugin.get_storage() as storage:
        if not 'bookmarks' in storage:
            storage['bookmarks'] = []
        if _id in storage['bookmarks']:
            xbmcgui.Dialog().notification(_("Error"), _("Documentation already in Bookmarks"))
        else:
            storage['bookmarks'].append(_id)


@plugin.action()
def remove_bookmark(params):
    with plugin.get_storage() as storage:
        storage['bookmarks'].pop(int(params.index))
    xbmc.executebuiltin('Container.Refresh')


@plugin.action()
def play(params):
    name = params.name
    youtube_id = params.get('youtube_id')

    if youtube_id and requests.head("http://www.youtube.com/oembed?url=http://www.youtube.com/watch?v={0}&format=json".format(youtube_id)).status_code == 200:
        video_url = "plugin://plugin.video.youtube/play/?video_id={0}".format(youtube_id)
    else:
        results = []
        for media in youtube_search(urllib.quote_plus(name)):
            label = media["label"]
            label2 = media["plot"]
            image = ""
            if media.get('art'):
                if media['art'].get('thumb'):
                    image = (media['art']['thumb'])
            listitem = xbmcgui.ListItem(label=label, label2=label2, iconImage=image)
            listitem.setProperty("path", media["file"])
            results.append(listitem)
        xbmc.executebuiltin("dialog.Close(busydialog)")
        title = "{0} \"{1}\"".format(_("Select mirror for"), name)
        dialog = DialogSelect("DialogSelect.xml", "", listing=results, title=title)
        dialog.doModal()
        result = dialog.result
        if not result:
            return
        video_url = result.getProperty("path")
    return Plugin.resolve_url(play_item={'path': video_url})


"""
@plugin.action()
def force_mirror(params):
    name = params.name

    xbmc.executebuiltin("ActivateWindow(busydialog)")

    results = []
    for media in youtube_search(name):
        label = media["label"]
        label2 = media["plot"]
        image = ""
        if media.get('art'):
            if media['art'].get('thumb'):
                image = (media['art']['thumb'])
        listitem = xbmcgui.ListItem(label=label, label2=label2, iconImage=image)
        listitem.setProperty("path", media["file"])
        results.append(listitem)

    xbmc.executebuiltin("dialog.Close(busydialog)")
    dialog = DialogSelect("DialogSelect.xml", "", listing=results)
    dialog.doModal()
    result = dialog.result
    if result:
        xbmc.executebuiltin('PlayMedia("%s")' % result.getProperty("path"))
"""


if __name__ == '__main__':
    plugin.run()
