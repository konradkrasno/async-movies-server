""" Provides tests for request_manager module. """

import pytest
import asyncio

from request_manager import RequestManager
from settings import DATABASES
from tests.testing_data import test_actor_query_result


@pytest.fixture
def req_man():
    return RequestManager(db_config=DATABASES["default"])


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


@pytest.mark.database
@pytest.mark.parametrize(
    "question, answer",
    [
        ("actor, Janusz Gajos", test_actor_query_result),
        (
            "custom, SELECT title FROM movies_metadata WHERE title='Pulp Fiction'",
            {"answer": [{"title": "Pulp Fiction"}]},
        ),
        ("wrong request", {"answer": "Wrong request content."}),
        (
            {
                "category": "custom",
                "query": "SELECT title FROM movies_metadata WHERE title='Pulp Fiction';",
            },
            {"answer": [{"title": "Pulp Fiction"}]},
        ),
    ],
)
def test_request_manager(req_man, question, answer):
    loop = asyncio.get_event_loop()
    response = loop.run_until_complete(req_man.entrypoint(question))
    loop.call_later(1, loop.stop)
    assert response == answer
