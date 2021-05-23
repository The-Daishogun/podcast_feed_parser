from bs4 import BeautifulSoup


class PodcastFeed:
    def __init__(self, feed_url: str) -> None:
        self.feed_url = feed_url
        self.feed_soup = BeautifulSoup(self.feed_url)

    def parse_itunes(self) -> dict:
        