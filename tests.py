import pytest
import asyncio
import json

from async_client import AsyncClient

HOST = "127.0.0.1"
PORT = 12345

messages = [
    {
        "message": "hey, what's up?",
        "content_type": "text",
        "encoding": "utf-8",
    },
    {
        "message": {
            "name": "Konrad",
            "message": "Hello world",
        },
        "content_type": "json",
        "encoding": "ascii",
    },
    {
        "message": b"Hello world",
        "content_type": "binary",
        "encoding": "ascii",
    }
]


def test_server() -> None:
    loop = asyncio.get_event_loop()
    for message in messages:
        async_client = AsyncClient(
            HOST,
            PORT,
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
    loop.close()


def test_server_with_wrong_data() -> None:
    pass
