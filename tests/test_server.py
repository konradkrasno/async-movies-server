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


@pytest.mark.server
def test_server_with_valid_data(loop) -> None:
    for message in valid_data:
        async_client = AsyncClient(
            SERVER["HOST"],
            SERVER["PORT"],
            loop=loop,
            test_request=message["message"],
            test_content_type=message["content_type"],
            test_encoding=message["encoding"],
        )
        try:
            header, result = async_client.run_client()
        except ConnectionRefusedError:
            raise ConnectionRefusedError(
                "Server is not running. Run start_server before start tests."
            )
        else:
            assert header == {
                "content_type": message["content_type"],
                "content_encoding": message["encoding"],
                "content_length": len(
                    json.dumps(message["message"]).encode(message["encoding"])
                )
                if message["content_type"] == "json"
                else len(message["message"]),
            }
            assert result == message["message"]


@pytest.mark.server
def test_server_with_wrong_data(loop) -> None:
    for message in wrong_data:
        async_client = AsyncClient(
            SERVER["HOST"],
            SERVER["PORT"],
            loop=loop,
            test_request=message["message"],
            test_content_type=message["content_type"],
            test_encoding=message["encoding"],
        )
        try:
            with pytest.raises(ValueError) as e:
                async_client.run_client()
        except ConnectionRefusedError:
            raise ConnectionRefusedError(
                "Server is not running. Run start_server before start tests."
            )
