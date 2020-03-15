""" All tests for hnet app """

from hnet import app, utils


def test_greeter() -> None:
    """ Silly test to test CI """
    assert utils.greeter("Tage") == "Hello Tage!"


def test_hello_world() -> None:
    """ Test the hello """
    assert app.hello_world() == "Hello world!"


def test_with_client(client) -> None:
    """ Test / with the app.test_client client from fixture"""
    root_response = client.get("/")
    assert root_response.data == b"Hello world!"
