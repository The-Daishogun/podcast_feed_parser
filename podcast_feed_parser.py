from bs4 import BeautifulSoup
import requests


class PodcastFeedParser:
    itunes_podcast_required_tags = [
        "title",
        "description",
        "itunes:image",
        "language",
        "itunes:category",
        "explicit",
        "category",
    ]
    itunes_podcast_recommended_tags = ["itunes:author", "link", "itunes:owner"]
    itunes_podcast_situational_tags = [
        "itunes:title",
        "itunes:type",
        "copyright",
        "itunes:new-feed-url",
        "itunes:block",
        "itunes:complete",
    ]
    itunes_episode_required_tags = ["title", "enclosure"]
    itunes_episode_recommended_tags = [
        "guid",
        "pubDate",
        "description",
        "itunes:duration",
        "link",
        "itunes:image",
        "itunes:explicit",
    ]
    itunes_episode_situational_tags = [
        "itunes:title",
        "itunes:episode",
        "itunes:season",
        "itunes:episodeType",
        "itunes:block",
        "",
    ]

    def __init__(self, feed_url: str) -> None:
        self.feed_url = feed_url
        self.feed_content = requests.get(feed_url).content
        self.feed_soup: BeautifulSoup = BeautifulSoup(
            self.feed_content, "xml", from_encoding="utf-8"
        )

    @property
    def is_itunes_compatible(self) -> bool:
        headings = self.feed_soup.find_all("rss")
        for heading in headings:
            if (
                heading["xmlns:itunes"] == "http://www.itunes.com/dtds/podcast-1.0.dtd"
                and heading["version"] == "2.0"
            ):
                return True
        return False

    def parse_itunes(self) -> dict:
        if self.is_itunes_compatible:
            parser_results = {
                key: self.feed_soup.find(key).text
                for key in self.itunes_podcast_required_tags
                if key != "category"
            }
            print(parser_results)
        else:
            return "podcast is not itunes compatible"
