""" Typed implementation of Sveriges Radio API interface

Original API reference at:
https://sverigesradio.se/api/documentation/v2/index.html
"""

from typing import Optional, List, Dict, Any
import logging
import warnings

import requests

log = logging.getLogger(__name__)

URL_BASE = "https://api.sr.se/api/v2"


def get_n_pages(n_items, pagesize=10):
    """ How many api-pages are needed to get n_items ? """
    return ((n_items - 1) // pagesize) + 1


class SrApiIter:
    """ Iterator for paginated SR API """

    def __init__(self, endpoint, data_key, max_pages=None, params=None):

        self.url = f"{URL_BASE}/{endpoint}"
        self.data_key = data_key

        # Default params
        self.params = {"format": "json", "pagination": True, "size": 10}
        self.page = 1
        self.max_pages = max_pages

        # If user supplied extra params, insert them now
        if params:
            for key, value in params.items():
                self.params[key] = value

    def __iter__(self):
        self.page = 1
        return self

    def __next__(self):

        # If max pages was passed and this page is beyond it, stop
        if self.max_pages and self.page > self.max_pages:
            raise StopIteration

        self.params["page"] = self.page
        # Something goes bad with utf-8 encoding here, .text is fine, .json not
        response = requests.get(url=self.url, params=self.params).json()
        data = response[self.data_key]

        if data:
            self.page += 1
        else:
            raise StopIteration

        return data


# pylint: disable=too-few-public-methods
class Episode:
    """ An episode of a program """

    def __init__(self, raw: Dict[str, Any]) -> None:
        self.id: int = int(raw["id"])  # pylint: disable=invalid-name
        self.title: str = raw["title"]
        self.description: str = raw["description"]
        self.program: Program = Program(raw["program"])
        self.raw = raw

        if "downloadpodfile" in raw.keys():
            self.url_audio = raw["downloadpodfile"]["url"]
        elif "broadcast" in raw.keys():
            # Get the first broadcastfile, might be incorrect
            # There's no exact time published for sorting that I can find
            self.url_audio = raw["broadcast"]["broadcastfiles"][0]["url"]
        else:
            self.url_audio = ""
            warnings.warn(f"Couldn't find an URL to audio file")

    def __str__(self):
        return f"Episode: id: {self.id} for program {self.program}"


class Program:
    """ An SR program """

    def __init__(self, raw: Dict[str, Any]) -> None:
        self.id = raw["id"]  # pylint: disable=invalid-name
        self.name = raw["name"]
        self.episodes: List[Episode] = []
        self.latest_episode: Optional[Episode] = None

    def __str__(self):
        return f"Program: name: {self.name} id: {self.id}"

    def refresh_episodes(self, n_episodes: int = 1) -> None:
        """ Refresh the episodes for this program """
        log.info(f"Getting {n_episodes} episodes for {self.name}")
        iter_pages = SrApiIter(
            endpoint="/episodes/index",
            data_key="episodes",
            params={"programid": self.id},
            max_pages=get_n_pages(n_items=n_episodes),
        )

        self.episodes = [
            Episode(raw_episode) for page in iter_pages for raw_episode in page
        ]
        self.latest_episode = self.episodes[0]


def get_all_programs_from_api() -> List[Program]:
    """ Get news and other programs """
    log.info(f"Getting all programs from API")
    # Get regular programs from paginated API
    programs: List[Program] = [
        Program(raw=raw_program)
        for page in SrApiIter(endpoint="/programs/index", data_key="programs")
        for raw_program in page
    ]
    # Get news programs, they come in a single page
    news: List[Program] = [
        Program(raw=raw_program)
        for raw_program in requests.get(
            url=f"{URL_BASE}/news", params={"format": "json"}
        ).json()["programs"]
    ]

    all_programs = dedupe_programs(news + programs)

    return all_programs


def dedupe_programs(programs: List[Program]) -> List[Program]:
    """ Deduplicate a list of programs """

    programs_unique: List[Program] = list()
    for program in programs:
        if not any(
            [prog for prog in programs_unique if prog.id == program.id]
        ):
            programs_unique.append(program)
    return programs_unique


def query_programs(name, programs: List[Program]) -> List[Program]:
    """ Simple "name in" query """
    matches = [
        program for program in programs if name.lower() in program.name.lower()
    ]
    log.info(f"Found {len(matches)} matches for programs named like {name}")
    return matches
