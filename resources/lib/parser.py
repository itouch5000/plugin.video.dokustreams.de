import re
import bs4


REGEX_YT_VIDEO = r"(?:youtube\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu\.be/)([^\"&?/\s]{11})"
REGEX_YT_PLAYLIST = r"(?:youtube\.com).+list=([^\"&?/\s]{34})"


class YtElement(object):
    def __init__(self):
        self.id = None
        self.title = None


def parse_yt_id(url):
    match = re.search(REGEX_YT_VIDEO, url)
    return match.group(1)


class Parser(object):
    def __init__(self, html):
        self.html = html
        self._videos = []
        self._playlists = []

    def parse(self):
        soup = bs4.BeautifulSoup(self.html, 'html5lib')

        match = soup.find_all('iframe', {'src': re.compile(REGEX_YT_VIDEO)})
        for index, item in enumerate(match):
            url = item["src"]

            e = YtElement()
            match_playlist = re.search(REGEX_YT_PLAYLIST, url)
            if match_playlist:
                e.id = match_playlist.group(1)
                e.title = item.get("title", "Playlist {0}".format(index + 1))
                self._playlists.append(e)
            else:
                e.id = parse_yt_id(url)
                e.title = item.get("title", "Video {0}".format(index + 1))
                self._videos.append(e)

        match = soup.find_all("a", {"class": "yotu-video", "data-videoid": True})
        for index, item in enumerate(match):
            e = YtElement()
            e.id = item["data-videoid"]
            e.title = item.get("data-title", "Video {0}".format(index + 1))
            self._videos.append(e)
        return self

    @property
    def videos(self):
        return self._videos

    @property
    def playlists(self):
        return self._playlists
