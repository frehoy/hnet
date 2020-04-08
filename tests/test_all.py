""" All tests for hnet app """

# pylint: disable=protected-access

from hnet import sr


def test_with_client(client) -> None:
    """ Test the app.test_client client fixture"""
    root_response = client.get("/")
    part = "Search SR programs by name "
    assert part in str(root_response.data)


def test_episode() -> None:
    """ Test the Episode constructor """

    raw = {
        "id": 123,
        "title": "fake episode",
        "description": "Some fake description",
        "program": {"id": 321, "name": "fake program"},
        "downloadpodfile": {"url": "http://some.fake.url"},
    }
    episode: sr.Episode = sr.Episode(raw)

    assert episode.id == 123
    assert episode.title == "fake episode"


def test_program() -> None:
    """ Test the Program constructor """
    raw = {"id": 1, "name": "fake program"}
    program = sr.Program(raw)

    assert program.id == 1
    assert program.name == "fake program"


def test_dedup_programs() -> None:
    """ Test that dedup programs works """

    prog_1 = sr.Program({"id": 1, "name": "fake program"})
    prog_1_dup = sr.Program({"id": 1, "name": "fake program"})
    prog_2 = sr.Program({"id": 2, "name": "fake program"})
    progs_w_duplicates = [prog_1, prog_1_dup, prog_2]
    progs_deduped = sr._dedupe_programs(progs_w_duplicates)
    assert len(progs_deduped) == 2


def test_get_n_pages():
    """ Test that the page math is correct """

    assert sr._get_n_pages(n_items=1, pagesize=10) == 1
    assert sr._get_n_pages(n_items=10, pagesize=10) == 1
    assert sr._get_n_pages(n_items=11, pagesize=10) == 2
    assert sr._get_n_pages(n_items=20, pagesize=10) == 2
    assert sr._get_n_pages(n_items=21, pagesize=10) == 3
    assert sr._get_n_pages(n_items=4, pagesize=2) == 2


def test_get_all_programs():
    """ Test getting all programs to check SR's APi working """
    _ = sr.get_all_programs_from_api()
