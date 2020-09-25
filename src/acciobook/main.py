import argparse
import logging
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from mutagen.easyid3 import EasyID3 as ID3
from mutagen.mp3 import EasyMP3 as MP3

BASE_URL = "https://hpaudiobooks.club/"

BOOK_TITLES = [
    "Harry Potter and the Philosopher's Stone",
    "Harry Potter and the Chamber of Secrets",
    "Harry Potter and the Prisoner of Azkaban",
    "Harry Potter and the Goblet of Fire",
    "Harry Potter and the Order of the Phoenix",
    "Harry Potter and the Half-Blood Prince",
    "Harry Potter and the Deathly Hallows",
]

BOOK_URLS = {
    "Stephen Fry": [
        "philosopher-stone-stephen-fry",
        "secrets-audiobook-stephen-fry",
        "prisoner-azkaban-audiobook-stephen-fry",
        "goblet-of-fire-audio-stephen-fry",
        "order-of-phoenix-audi-stephen-fry",
        "half-blood-prince-audiobook-stephen-fry",
        "deathly-hallow-audiobook-stephen-fry",
    ],
    "Jim Dale": [
        "philosopher-stone-audiobooks-jim-dale",
        "hp-secret-jim-dale",
        "prisoner-azkaban-book-jim-dale",
        "goblet-audiobooks-jim-dale",
        "phoenix-audiobook-jim-dale",
        "half-prince-jim-dale",
        "deathly-hallow-jim-dale",
    ],
}


class Parser(HTMLParser):
    title = None
    p = False
    done = False

    def __init__(self, start_chapter: int, end_chapter: Optional[int]):
        super().__init__()
        self.start = start_chapter
        self.end = end_chapter

    def handle_starttag(self, tag, attrs):
        if self.done:
            return

        if tag == "p":
            self.p = True
            self.title = None
        elif tag == "source":
            attr_dict = parse_attrs(attrs)
            if attr_dict["type"] == "audio/mpeg":
                if self.title is None:
                    logging.error("ERROR: Missing title")
                    return

                # Some of the pages have typos, so account for those when parsing the
                # chapter string
                match = re.search(
                    r"“(?:Chapter|Chpater) (\d+)\s*[–-]\s*([^”]+)”", self.title
                )
                if match is None:
                    logging.error(
                        "ERROR: Couldn't parse chapter number and name from '%s'",
                        self.title,
                    )
                    return

                chapter = int(match.group(1))
                if chapter < self.start:
                    return

                if self.end and chapter > self.end:
                    self.done = True
                    return

                name = match.group(2)
                url = attr_dict["src"]
                output = Path("{:02} {}.mp3".format(chapter, name))
                src = AudioSource(chapter, url)
                src.download(output)

    def handle_endtag(self, tag):
        if self.done:
            return

        if tag == "p":
            self.p = False
            self.title = None

    def handle_data(self, data):
        if self.done:
            return

        if self.p and not self.title:
            self.title = data


@dataclass
class AudioSource:
    chapter: int
    url: str

    def download(self, output: Path) -> None:
        logging.info("Downloading chapter %s from %s", self.chapter, self.url)
        with requests.get(self.url, stream=True) as r:
            with output.open("wb") as f:
                for chunk in r.iter_content(chunk_size=16 * 1024):
                    f.write(chunk)

        audio = MP3(output)
        tags = audio.tags or ID3()
        tags["tracknumber"] = [self.chapter]
        audio.tags = tags
        audio.save()

        print(f"Downloaded {output}")


def parse_attrs(attrs: List[Tuple[str, str]]) -> Dict[str, str]:
    return {attr[0]: attr[1] for attr in attrs}


def choose_from_list(options: List[str], prompt: str) -> str:
    print(prompt)
    for i, opt in enumerate(options):
        print(f"[{i+1}] {opt}")

    while True:
        try:
            value = input("Selection: ")
            if value == "":
                continue

            index = int(value)
            if index <= 0 or index > len(options):
                print("Invalid selection")
                continue

            return options[index - 1]
        except ValueError:
            print("Invalid selection")


def ask_for_int(prompt: str) -> Optional[int]:
    while True:
        try:
            value = input(f"{prompt}: ")
            if value == "":
                return None

            parsed = int(value)
            if parsed <= 0:
                print("Invalid input")
                continue

            return parsed
        except ValueError:
            print("Invalid input")


def scrape(
    book_number: int, author: str, start_chapter: int, end_chapter: Optional[int]
) -> None:
    parser = Parser(start_chapter, end_chapter)
    url = BASE_URL + BOOK_URLS[author][book_number]
    page = 1
    while not parser.done:
        r = requests.get(f"{url}/{page}/")

        if r.status_code != 200:
            logging.error("ERROR: Received status code %s; quitting...", r.status_code)
            return

        if page > 1 and r.history and r.history[0].is_redirect:
            # When a page is requested that does not exist, it redirects back to the
            # first page. We can use this to detect when we've reached the last page.
            # Note that putting `1` as the page number in the URL *also* redirects back
            # to the root URL (sans page number), so we also check for this case.
            print("Done.")
            return

        parser.feed(r.text)
        page += 1


def run() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print more output"
    )

    args = parser.parse_args()

    level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(format="%(message)s", level=level)

    book = choose_from_list(BOOK_TITLES, "Which book do you want to download?")
    book_number = BOOK_TITLES.index(book)
    author = choose_from_list(list(BOOK_URLS.keys()), "Select a narrator.")

    start_chapter = ask_for_int("Start chapter (Default: 1)")
    if not start_chapter:
        start_chapter = 1

    end_chapter = ask_for_int("End chapter (Leave empty to download all chapters)")
    scrape(book_number, author, start_chapter, end_chapter)
