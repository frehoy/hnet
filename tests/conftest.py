""" pytest fixtures """
import pytest  # type: ignore

from hnet import app


@pytest.fixture
def client():
    """ Client fixture

    See: https://flask.palletsprojects.com/en/1.1.x/testing/
    """
    app.app.config["TESTING"] = True
    with app.app.test_client() as test_client:
        yield test_client
