import re
import bs4


REGEX_YT_VIDEO = r"(?:youtube\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu\.be/)([^\"&?/\s]{11})"


class Video(object):
    def __init__(self):
        self.id = None


def parse_yt_id(url):
    match = re.search(REGEX_YT_VIDEO, url)
    return match.group(1)


def parse_videos(html):
    soup = bs4.BeautifulSoup(html, 'html5lib')
    videos = []

    match = soup.find_all('iframe', {'src': re.compile(REGEX_YT_VIDEO)})
    for i in match:
        url = i["src"]
        v = Video()
        v.id = parse_yt_id(url)
        videos.append(v)

    match = soup.find_all("a", {"class": "yotu-video", "data-videoid": True})
    for i in match:
        v = Video()
        v.id = i["data-videoid"]
        videos.append(v)

    return videos
