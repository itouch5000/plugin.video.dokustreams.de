import unittest

from resources.lib.parser import parse_yt_id


class ParserTests(unittest.TestCase):
    def test_parse_yt_video_id(self):
        cases = {
            "http://www.youtube.com/watch?v=0zM3nApSvMg&feature=feedrec_grec_index": "0zM3nApSvMg",
            "http://www.youtube.com/user/IngridMichaelsonVEVO#p/a/u/1/QdK8U-VIH_o": "QdK8U-VIH_o",
            "http://www.youtube.com/v/0zM3nApSvMg?fs=1&amp;hl=en_US&amp;rel=0": "0zM3nApSvMg",
            "http://www.youtube.com/watch?v=0zM3nApSvMg#t=0m10s": "0zM3nApSvMg",
            "http://www.youtube.com/embed/0zM3nApSvMg?rel=0": "0zM3nApSvMg",
            "http://www.youtube.com/watch?v=0zM3nApSvMg": "0zM3nApSvMg",
            "http://youtu.be/0zM3nApSvMg": "0zM3nApSvMg",
            "https://youtube.com/watch?v=0zM3nApSvMg#t=0m10s": "0zM3nApSvMg",
        }
        for url, yt_video_id in cases.items():
            parsed_video_id = parse_yt_id(url)
            self.assertEqual(yt_video_id, parsed_video_id)


if __name__ == '__main__':
    unittest.main()
