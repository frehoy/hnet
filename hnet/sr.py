""" Typed implementation of Sveriges Radio API interface

The idea is to provide an interface through classes so we aren't
passing dicts around blindly, hoping they have the right fields.
"""

import logging
from typing import Optional, List, Dict, Any

import requests

import hnet

logging.basicConfig(format=hnet.LOGFORMAT, level=logging.DEBUG)
log = logging.getLogger(__name__)

URL_BASE = "https://api.sr.se/api/v2"


def get_n_pages(n_items, pagesize=10):
    """ How many api-pages are needed to get n_items ? """
    return (n_items // pagesize) + 1


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


class Episode:
    """ Episode class """

    def __init__(self, raw: Dict[str, Any]) -> None:
        self.id: int = int(raw["id"])  # pylint: disable=invalid-name
        self.title: str = raw["title"]
        self.description: str = raw["description"]
        self.program: Program = Program(
            program_id=raw["program"]["id"], name=raw["program"]["name"]
        )

        if "downloadpodfile" in raw.keys():
            self.url_audio = raw["downloadpodfile"]["url"]
        elif "broadcast" in raw.keys():
            # Get the first broadcastfile, might be incorrect
            self.url_audio = raw["broadcast"]["broadcastfiles"][0]["url"]
        else:
            raise RuntimeError(f"Couldn't find an URL to audio file")

    def __str__(self):
        return f"Episode: id: {self.id} for program {self.program}"


class Program:
    """ An SR program """

    def __init__(self, program_id: int, name: str) -> None:
        self.id = program_id  # pylint: disable=invalid-name
        self.name = name
        self.episodes: List[Episode] = []
        self.latest_episode: Optional[Episode] = None
        self.n_episodes = 2

    def __str__(self):
        return f"Program: name: {self.name} id: {self.id}"

    def refresh_episodes(self) -> None:
        """ Refresh the episodes for this program """

        iter_pages = SrApiIter(
            endpoint="/episodes/index",
            data_key="episodes",
            params={"programid": self.id},
            max_pages=get_n_pages(n_items=self.n_episodes),
        )

        self.episodes = [
            Episode(raw_episode) for page in iter_pages for raw_episode in page
        ]


def get_all_programs_from_api() -> List[Program]:
    """ Get news and other programs """
    log.debug(f"Getting all programs from API")
    # Get regular programs from paginated API
    programs: List[Program] = [
        Program(program_id=program["id"], name=program["name"])
        for page in SrApiIter(endpoint="/programs/index", data_key="programs")
        for program in page
    ]
    # Get news programs, they come in a single page
    news: List[Program] = [
        Program(program_id=raw_program["id"], name=raw_program["name"])
        for raw_program in requests.get(
            url=f"{URL_BASE}/news", params={"format": "json"}
        ).json()["programs"]
    ]

    return news + programs


def query_programs(name, programs: List[Program]) -> List[Program]:
    """ Simple "name in" query """
    matches = [
        program for program in programs if name.lower() in program.name.lower()
    ]
    log.info(f"Found {len(matches)} matches for programs named like {name}")
    return matches


def main():
    """ Dev stuff """

    term = "ekot"
    all_programs = get_all_programs_from_api()
    matching_programs = query_programs(name=term, programs=all_programs)
    for program in matching_programs:
        program.refresh_episodes()
        for episode in program.episodes:
            print(episode)


if __name__ == "__main__":
    main()
