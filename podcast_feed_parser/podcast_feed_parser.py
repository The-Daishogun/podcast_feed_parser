from bs4 import BeautifulSoup
import requests
from typing import Union
import hashlib


def handle_explicit(value: str) -> Union[bool, None]:
    if value is not None:
        if value == "no":
            return False
        elif value == "yes":
            return True
    return None


class PodcastFeedParser:
    rss2_podcast_required_tags = ["title", "description", "link"]
    rss2_podcast_optional_tags = [
        "language",
        "managingEditor",
        "webMaster",
        "pubDate",
        "lastBuildDate",
        "copyright",
        "generator",
        "docs",
        "cloud",
        "ttl",
        "textInput",
        "skipHours",
        "skipDays",
    ]
    special_podcast_tags = ["image", "category", "itunes:category", "itunes:owner"]
    rss2_episode_required_tags = [
        "title",
        "link",
        "description",
        "author",
        "category",
        "comments",
        "pubDate",
    ]
    rss2_episode_special_tags = [
        "enclosure",
        "guid",
        "itunes:image",
        "content:encoded",
    ]
    itunes_podcast_specific_tags = [
        "itunes:image",
        "itunes:explicit",
        "itunes:author",
        "itunes:title",
        "itunes:type",
        "itunes:new-feed-url",
        "itunes:block",
        "itunes:complete",
        "itunes:subtitle",
        "itunes:summary",
        "itunes:keywords",
    ]
    itunes_episode_specific_tags = [
        "itunes:image",
        "itunes:explicit",
        "itunes:title",
        "itunes:episode",
        "itunes:season",
        "itunes:episodeType",
        "itunes:block",
        "itunes:summary",
        "itunes:subtitle",
        "itunes:duration",
        "itunes:keywords",
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

    def parse_podcast(self) -> dict:
        podcast_results = {
            key: self.feed_soup.find(key)
            for key in self.rss2_podcast_required_tags
            + self.rss2_podcast_optional_tags
            + self.itunes_podcast_specific_tags
            if key != "category"
        }
        for key, value in podcast_results.items():
            if key == "itunes:image":
                podcast_results[key] = value["href"]
            elif key == "itunes:explicit":
                print(value.text if value is not None else value)
                podcast_results[key] = handle_explicit(
                    value.text if value is not None else value
                )
            else:
                podcast_results[key] = value.text if value is not None else value
        for key in self.special_podcast_tags:
            if key == "image":
                item = self.feed_soup.find("image")
                image_dic = {
                    "image_url": item.find("url"),
                    "image_title": item.find("title"),
                    "image_link": item.find("link"),
                    "image_width": item.find("width"),
                    "image_height": item.find("height"),
                    "image_description": item.find("description"),
                }
                for key2, value in image_dic.items():
                    image_dic[key2] = value.text if value is not None else value
                podcast_results.update(image_dic)
            if key == "category":
                categories = []
                for item in self.feed_soup.find_all("category"):
                    if item.text.strip() == "":
                        categories.append(item["text"])
                    else:
                        categories.append(item.text)
                podcast_results.update({"categories": categories})
            if key == "itunes:category":
                category = self.feed_soup.find("itunes:category")
                subcategory = category.find("itunes:category")
                podcast_results.update(
                    {
                        key: [
                            category["text"],
                            subcategory["text"]
                            if subcategory is not None
                            else subcategory,
                        ]
                    }
                )
            if key == "itunes:owner":
                item = self.feed_soup.find("itunes:owner")
                podcast_results.update(
                    {
                        "itunes_owner_name": item.find("itunes:name").text,
                        "itunes_owner_email": item.find("itunes:email").text,
                    }
                )
        return podcast_results

    def parse_episodes(self) -> list:
        # get items
        episodes = []
        for item in self.feed_soup.find_all("item"):
            episode = {
                key: item.find(key)
                for key in self.itunes_episode_specific_tags
                + self.rss2_episode_required_tags
            }
            for key, value in episode.items():
                if key == "itunes:explicit":
                    episode[key] = handle_explicit(
                        value.text if value is not None else value
                    )
                else:
                    episode[key] = value.text if value is not None else value
            for key in self.rss2_episode_special_tags:
                if key == "guid":
                    guid = item.find("guid")
                    episode.update(
                        {
                            "guid_is_permalink": guid["isPermaLink"],
                            "guid": guid.text,
                        }
                    )
                if key == "enclosure":
                    enclosure = item.find("enclosure")
                    episode.update(
                        {
                            "enclosure_url": enclosure["url"],
                            "enclosure_length": enclosure["length"],
                            "enclosure_type": enclosure["type"],
                        }
                    )
                if key == "itunes:image":
                    image = item.find("itunes:image")
                    if image is not None:
                        episode.update({"itunes:image": image["href"]})

                if key == "content:encoded":
                    episode.update(
                        {"content:encoded": str(item.find("content:encoded"))[17:-18]}
                    )
            episodes.append(episode)
        return episodes

    def parse_all(self) -> dict:
        if self.is_itunes_compatible:
            parser_results = self.parse_podcast()
            parser_results.update({"episodes": self.parse_episodes()})
            return parser_results
        else:
            raise Exception("podcast is not itunes compatible")

    def feed_hash(self):
        hashed = hashlib.md5(self.feed_content)
        return hashed.hexdigest()
