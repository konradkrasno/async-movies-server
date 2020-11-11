import pytest
import asyncio
from datetime import datetime

from async_client import AsyncClient

HOST = "127.0.0.1"
PORT = 12345

messages = [
    "hey, what's up?",
    "hello everyone!",
    # "Well, I'm the crawlin' king snake And I rule my den I'm the crawlin' king snake And I rule my den",
]


def test_server() -> None:
    loop = asyncio.get_event_loop()
    for message in messages:
        async_client = AsyncClient(HOST, PORT, loop=loop, test_data=message)
        try:
            result = async_client.run_client()
        except ConnectionRefusedError:
            raise ConnectionRefusedError(
                "Server is not running. Run start_server before start tests."
            )
        else:
            assert result == message
    loop.close()
