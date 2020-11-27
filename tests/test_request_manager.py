""" Provides tests for request_manager module. """

import pytest
import asyncio

from request_manager import RequestManager
from settings import DATABASES


@pytest.fixture
def req_man():
    return RequestManager(db_config=DATABASES["docker"])


@pytest.mark.parametrize(
    "req, result",
    [
        (
            "director, Quentin Tarantino",
            {
                "category": "director",
                "query": "Quentin Tarantino",
            },
        ),
        (
            "custom, SELECT * FROM actors;",
            {
                "category": "custom",
                "query": "SELECT * FROM actors;",
            },
        ),
        (
            "actor",
            {
                "category": "wrong_request",
            },
        ),
        (
            ["wrong request type"],
            {
                "category": "wrong_type",
            },
        ),
    ],
)
def test_process_request(req, result):
    assert RequestManager.process_request(req) == result


def test_request_manager_with_valid_request(req_man):
    # TODO finish
    loop = asyncio.get_event_loop()
    request = "get_all_polish_movies"
    response = loop.run_until_complete(req_man.entrypoint(request))
    # TODO add assertion
    print("response:", response)
    assert type(response) == dict
    loop.close()


def test_request_manager_with_unknown_request(req_man):
    # TODO finish
    loop = asyncio.get_event_loop()
    request = "unknown_request"
    response = loop.run_until_complete(req_man.entrypoint(request))
    assert response == {"answer": "Unknown request"}
    loop.close()
