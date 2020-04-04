import re
import bs4
import json
import requests

try:
    # python 3
    from urllib.parse import urlencode, parse_qsl, urlsplit, unquote, quote_plus
except ModuleNotFoundError:
    # python 2
    from urlparse import parse_qsl, urlsplit
    from urllib import urlencode, unquote, quote_plus

try:
    # python 3
    from html import unescape
except ModuleNotFoundError:
    # python 2
    from HTMLParser import HTMLParser
    unescape = HTMLParser().unescape

import xbmc
import xbmcgui
import xbmcplugin

from resources.lib import plugin
from resources.lib.language import Language
from resources.lib.settings import get_setting


BASE_URL = 'http://dokustreams.de/wp-json/wp/v2'
PER_PAGE = get_setting('per_page')


def page_from_url(url):
    params = dict(parse_qsl(urlsplit(url).query))
    page = int(params.get('page', 1))
    return page


def list_videos(url, enable_bookmark=True):
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
                (Language.add_to_bookmarks,
                 'XBMC.RunPlugin({0})'.format(plugin.get_url(action='add_bookmark', id=_id))),
            )
        context_menu += [
            (Language.show_tags,
             'XBMC.Container.Update({0})'.format(plugin.get_url(action='tags_by_post', id=_id))),
            (Language.show_categories,
             'XBMC.Container.Update({0})'.format(plugin.get_url(action='categories_by_post', id=_id))),
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
            'label': '[COLOR blue]{0}[/COLOR]'.format(Language.next_page),
            'url': plugin.get_url(action='posts_by_url', url=next_url),
        })
    return listing


def list_tags(url):
    json_data = requests.get(url).json()
    listing = []
    for i in json_data:
        name = HTMLParser().unescape(i.get('name'))
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
            'label': '[COLOR blue]{0}[/COLOR]'.format(Language.next_page),
            'url': plugin.get_url(action='tags_by_url', url=next_url),
        })
    return listing


def list_categories(url):
    json_data = requests.get(url).json()
    listing = []
    for i in json_data:
        name = HTMLParser().unescape(i.get('name'))
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
            'label': '[COLOR blue]{0}[/COLOR]'.format(Language.next_page),
            'url': plugin.get_url(action='categories_by_url', url=next_url),
        })
    return listing


def youtube_search(query):
    properties = [
        "dateadded", "file", "lastplayed", "plot", "title", "art", "playcount", "streamdetails", "director", "resume",
        "runtime", "plotoutline", "sorttitle", "cast", "votes", "trailer", "year", "country", "studio", "genre", "mpaa",
        "rating", "tagline", "writer", "originaltitle", "imdbnumber", "premiered", "episode", "showtitle", "firstaired",
        "watchedepisodes", "duration", "season"
    ]
    data = {
        "jsonrpc": "2.0",
        "method": "Files.GetDirectory",
        "id": 1,
        "params": {
            "properties": properties,
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


def build_url(path, params=None):
    if not params:
        params = dict()
    params.setdefault('per_page', PER_PAGE)
    url = '{0}/{1}?{2}'.format(BASE_URL, path, urlencode(params))
    return url


def edit_url(url, new_params):
    parsed = urlsplit(url)
    params = dict(parse_qsl(urlsplit(url).query))
    params.update(new_params)
    new_url = '{0}://{1}{2}?{3}'.format(parsed.scheme, parsed.netloc, parsed.path, urlencode(params))
    return new_url


def parse_ids_content(content):
    soup = bs4.BeautifulSoup(content, 'html5lib')
    yt_playlists = []
    yt_videos = []
    match = soup.find_all('div', {'class': 'lyMe'})
    for i in match:
        if 'playlist' in i['class']:
            yt_pid = i['id'][4:]
            yt_pimg = soup.find('div', {'id': 'lyte_{0}'.format(yt_pid)})['data-src']
            yt_pimg = unquote(yt_pimg)
            yt_vid = re.findall('/vi/([^\"&?\/\ ]{11})/', yt_pimg)[0]
            yt_playlists.append((yt_pid, yt_vid))  # contains tuple with (id, image_id)
        else:
            yt_vid = i['id'][4:]
            yt_videos.append(yt_vid)  # contains id
    return yt_playlists, yt_videos


def root(params):
    xbmcplugin.addDirectoryItem(
        plugin.handle,
        plugin.get_url(action='all_posts'),
        xbmcgui.ListItem(Language.documentations),
        isFolder=True
    )
    xbmcplugin.addDirectoryItem(
        plugin.handle,
        plugin.get_url(action='multiple_videos_playlists', id=15092, name='Kurzdokus und Reportagen'),
        xbmcgui.ListItem(Language.short_documentations),
        isFolder=True
    )
    xbmcplugin.addDirectoryItem(
        plugin.handle,
        plugin.get_url(action='all_tags'),
        xbmcgui.ListItem(Language.tags),
        isFolder=True
    )
    xbmcplugin.addDirectoryItem(
        plugin.handle,
        plugin.get_url(action='all_categories'),
        xbmcgui.ListItem(Language.categories),
        isFolder=True
    )
    xbmcplugin.addDirectoryItem(
        plugin.handle,
        plugin.get_url(action='search_posts'),
        xbmcgui.ListItem(Language.search_documentations),
        isFolder=True
    )
    xbmcplugin.addDirectoryItem(
        plugin.handle,
        plugin.get_url(action='search_tags'),
        xbmcgui.ListItem(Language.search_tags),
        isFolder=True
    )
    xbmcplugin.addDirectoryItem(
        plugin.handle,
        plugin.get_url(action='search_categories'),
        xbmcgui.ListItem(Language.search_categories),
        isFolder=True
    )
    xbmcplugin.addDirectoryItem(
        plugin.handle,
        plugin.get_url(action='bookmarks'),
        xbmcgui.ListItem(Language.bookmarks),
        isFolder=True
    )
    xbmcplugin.endOfDirectory(plugin.handle)


def all_posts(params):
    url = build_url('posts')
    return list_videos(url)


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
            'label': "{0} {1}".format(Language.playlist, index + 1),
            'thumb': image,
            'is_playable': False,
            'url': "plugin://plugin.video.youtube/playlist/{0}/".format(yt_pid),
        })
    for index, yt_vid in enumerate(yt_videos):
        image = "https://i.ytimg.com/vi/{0}/hqdefault.jpg".format(yt_vid)
        listing.append({
            'label': "{0} {1}".format(Language.video, index + 1),
            'thumb': image,
            'is_playable': True,
            'url': plugin.get_url(action='play', youtube_id=yt_vid, name=title),
        })
    return listing


def all_tags(params):
    url = build_url('tags')
    return list_tags(url)


def all_categories(params):
    url = build_url('categories')
    return list_categories(url)


def search_posts(params):
    dialog = xbmcgui.Dialog()
    query = dialog.input(Language.search_documentations)
    if query:
        url = build_url('posts', {'search': query})
        return list_videos(url)


def search_tags(params):
    dialog = xbmcgui.Dialog()
    query = dialog.input(Language.search_tags)
    if query:
        url = build_url('tags', {'search': query})
        return list_tags(url)


def search_categories(params):
    dialog = xbmcgui.Dialog()
    query = dialog.input(Language.search_categories)
    if query:
        url = build_url('categories', {'search': query})
        return list_categories(url)


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
            (Language.remove_from_bookmarks,
             'XBMC.RunPlugin({0})'.format(plugin.get_url(action='remove_bookmark', index=index))),
        )
        item['context_menu'] += old_context
    return listing


def posts_by_url(params):
    url = params.url
    return list_videos(url)


def tags_by_url(params):
    url = params.url
    return list_tags(url)


def categories_by_url(params):
    url = params.url
    return list_categories(url)


def posts_by_tag(params):
    _id = params.get('id')
    url = build_url('posts', {'tags': _id})
    return list_videos(url)


def posts_by_category(params):
    _id = params.get('id')
    url = build_url('posts', {'categories': _id})
    return list_videos(url)


def tags_by_post(params):
    post_id = params.id
    url = build_url('tags', {'post': post_id})
    return list_tags(url)


def categories_by_post(params):
    post_id = params.id
    url = build_url('categories', {'post': post_id})
    return list_categories(url)


def add_bookmark(params):
    _id = params.id
    with plugin.get_storage() as storage:
        if not 'bookmarks' in storage:
            storage['bookmarks'] = []
        if _id in storage['bookmarks']:
            xbmcgui.Dialog().notification(Language.error, Language.documentation_already_in_bookmarks)
        else:
            storage['bookmarks'].append(_id)


def remove_bookmark(params):
    with plugin.get_storage() as storage:
        storage['bookmarks'].pop(int(params.index))
    xbmc.executebuiltin('Container.Refresh')


def play(params):
    name = params.name
    youtube_id = params.get('youtube_id')

    if youtube_id and requests.head("http://www.youtube.com/oembed?url=http://www.youtube.com/watch?v={0}&format=json".format(youtube_id)).status_code == 200:
        video_url = "plugin://plugin.video.youtube/play/?video_id={0}".format(youtube_id)
    else:
        results = []
        for media in youtube_search(quote_plus(name)):
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
        title = "{0} \"{1}\"".format(Language.select_mirror_for, name)
        dialog = DialogSelect("DialogSelect.xml", "", listing=results, title=title)
        dialog.doModal()
        result = dialog.result
        if not result:
            return
        video_url = result.getProperty("path")
    return Plugin.resolve_url(play_item={'path': video_url})
