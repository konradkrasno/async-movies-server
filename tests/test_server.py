""" Provides tests of working server and client. """

import pytest
import asyncio
import json

from async_client import AsyncClient
from tests.testing_data import valid_data, wrong_data
from settings import SERVER


@pytest.fixture
def loop() -> asyncio.AbstractEventLoop:
    return asyncio.get_event_loop()


@pytest.mark.database
@pytest.mark.server
def test_server_with_valid_data(loop) -> None:
    for message in valid_data:
        async_client = AsyncClient(
            SERVER["HOST"],
            SERVER["PORT"],
            loop=loop,
        )
        try:
            header, result = async_client.run_client(
                message["message"], message["content_type"], message["encoding"]
            )

        except ConnectionRefusedError:
            raise ConnectionRefusedError(
                "Server is not running. Run app_server.py before start tests."
            )
        else:
            assert header == {
                "content_type": "json",
                "content_encoding": "utf-8",
                "content_length": len(
                    json.dumps(message["result"]).encode(message["encoding"])
                )
            }
            assert result == message["result"]


@pytest.mark.server
def test_server_with_wrong_data(loop) -> None:
    for message in wrong_data:
        async_client = AsyncClient(
            SERVER["HOST"],
            SERVER["PORT"],
            loop=loop,
        )
        try:
            with pytest.raises(ValueError) as e:
                async_client.run_client(
                    message["message"], message["content_type"], message["encoding"]
                )
        except ConnectionRefusedError:
            raise ConnectionRefusedError(
                "Server is not running. Run app_server.py before start tests."
            )
