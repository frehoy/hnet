""" Sveriges Radio API interface

Docs here: https://sverigesradio.se/api/documentation/v2/index.html
"""

import os
import json

from typing import List, Dict, Any
import requests

URL_BASE = "https://api.sr.se/api/v2"


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
        response = requests.get(url=self.url, params=self.params).json()
        data = response[self.data_key]

        if data:
            self.page += 1
        else:
            raise StopIteration

        return data


def get_all_programs_from_api() -> List[Any]:
    """ Get news and other programs """

    # Get regular programs
    programs: List[Any] = [
        program
        for page in SrApiIter(endpoint="/programs/index", data_key="programs")
        for program in page
    ]
    # News programs are listed in their own endpoint w/o pagination
    news: List[Any] = requests.get(
        url=f"{URL_BASE}/news", params={"format": "json"}
    ).json()["programs"]

    return news + programs


def load_programs() -> Dict[str, Any]:
    """ If we have cached programs, return them. Otherwise fetch them """

    # Load cached programs if we have them
    if os.path.isfile("programs.json"):
        print(f"Loading programs from json")
        with open("programs.json", "r") as f:
            programs = json.load(f)
    # Fetch if we don't
    else:
        print(f"Didn't find any local programs, refetching")
        programs = get_all_programs_from_api()
        with open("programs.json", "w") as f:
            json.dump(programs, f, indent=4)
    return programs


def get_n_pages(n_items, pagesize=10):
    """ How many api-pages are needed to get n_items ? """
    return (n_items // pagesize) + 1


def get_episodes(program_id, n_episodes=1):
    """ Get episodes for a program """
    iter_pages = SrApiIter(
        endpoint="/episodes/index",
        data_key="episodes",
        params={"programid": program_id},
        max_pages=get_n_pages(n_items=n_episodes),
    )
    episodes = [episode for page in iter_pages for episode in page]
    return episodes[0:n_episodes]


def query_programs(programs, name) -> List[Any]:
    """ Get programs matching a name """
    return [
        program
        for program in programs
        if name.lower() in program["name"].lower()
    ]


def get_programs_with_episodes(name: str) -> None:
    """ Get list of dicts of programs with latest episodes attached"""
    for program in query_programs(programs=load_programs(), name=name):
        _ = get_episodes(program_id=program["id"])
