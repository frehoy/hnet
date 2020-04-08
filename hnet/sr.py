""" Typed implementation of Sveriges Radio API interface

Original API reference at:
https://sverigesradio.se/api/documentation/v2/index.html
"""

from typing import Optional, List, Dict, Any
import logging
import warnings
import requests

# Hook into the parent applications logger.
# Not cool as it's not portable but it works for now.
log = logging.getLogger("hnet.app")

URL_BASE = "http://api.sr.se/api/v2"


class _SrApiIter:
    """ Iterator for paginated SR API """

    default_pagesize = 100

    def __init__(self, endpoint, data_key, n_items=None, params=None):

        self.url = f"{URL_BASE}/{endpoint}"
        self.data_key = data_key

        # If n_items passed, set self.n_items
        self.n_items: Optional[int] = n_items if n_items else None

        self.pagesize: int
        if self.n_items and self.n_items <= _SrApiIter.default_pagesize:
            self.pagesize = self.n_items
        else:
            self.pagesize = _SrApiIter.default_pagesize

        # If self.n_items is set, set self.max_pages
        self.max_pages: Optional[int] = _get_n_pages(
            self.n_items, pagesize=self.pagesize
        ) if self.n_items else None

        # Default params
        self.params = {
            "format": "json",
            "pagination": True,
            "size": self.pagesize,
        }
        self.page = 1

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
        response = requests.get(url=self.url, params=self.params)
        log.debug(response.url)
        response_json = response.json()
        data = response_json[self.data_key]

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
        self.program_name = raw["program"]["name"]
        log.debug(f"Initalised {self}")

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
        return (
            f"Episode: id: {self.id} name: {self.title} "
            f"program {self.program_name}"
        )


class Program:
    """ An SR program """

    def __init__(self, raw: Dict[str, Any]) -> None:
        self.id = raw["id"]  # pylint: disable=invalid-name
        self.name = raw["name"]
        self.episodes: List[Episode] = []
        self.latest_episode: Optional[Episode] = None
        log.debug(f"Initalised {self}")

    def __str__(self):
        return f"Program: name: {self.name} id: {self.id}"

    def refresh_episodes(self, n_episodes: int = 1) -> None:
        """ Refresh the episodes for this program """
        log.info(f"Getting {n_episodes} episodes for {self.name}")
        iter_pages = _SrApiIter(
            endpoint="/episodes/index",
            data_key="episodes",
            params={"programid": self.id},
            n_items=n_episodes,
        )

        self.episodes = [
            Episode(raw_episode) for page in iter_pages for raw_episode in page
        ]
        self.latest_episode = self.episodes[0]


def _get_n_pages(n_items: int, pagesize: int) -> int:
    """ How many api-pages are needed to get n_items ? """
    return ((n_items - 1) // pagesize) + 1


def _dedupe_programs(programs: List[Program]) -> List[Program]:
    """ Deduplicate a list of programs """

    programs_unique: List[Program] = list()
    for program in programs:
        if not any(
            [prog for prog in programs_unique if prog.id == program.id]
        ):
            programs_unique.append(program)

    n_removed = len(programs) - len(programs_unique)
    log.debug(f"Dedup removed {n_removed} duplicate programs")
    return programs_unique


def get_all_programs_from_api() -> List[Program]:
    """ Get news and other programs """
    log.info(f"Fetching all programs from API")
    # Get regular programs from paginated API
    log.debug(f"Fetching programs")
    programs: List[Program] = [
        Program(raw=raw_program)
        for page in _SrApiIter(endpoint="/programs/index", data_key="programs")
        for raw_program in page
    ]
    # Get news programs, they come in a single page
    log.debug(f"Fetching news programs")
    news: List[Program] = [
        Program(raw=raw_program)
        for raw_program in requests.get(
            url=f"{URL_BASE}/news", params={"format": "json"}
        ).json()["programs"]
    ]

    all_programs = _dedupe_programs(news + programs)
    log.info(f"Fininshed fetching all programs from API")

    return all_programs


def query_programs(name, programs: List[Program]) -> List[Program]:
    """ Simple "name in" query """
    matches = [
        program for program in programs if name.lower() in program.name.lower()
    ]
    log.info(f"Found {len(matches)} matches for programs named like {name}")
    return matches
