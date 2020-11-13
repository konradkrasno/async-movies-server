import pytest
import asyncio
import json

from async_client import AsyncClient
from test_data import valid_data, wrong_data
from request_manager import RequestManager
from app_server import HOST, PORT

with open("secure.json", "r") as file:
    secure = json.load(file)
DSN = f'postgres://postgres:{secure["PG_PASSWORD"]}@172.17.0.2/postgres'

server_running_required = pytest.mark.skipif(False, reason="Server running required.")


@pytest.fixture
def loop() -> asyncio.AbstractEventLoop:
    return asyncio.get_event_loop()


@server_running_required
def test_server_with_valid_data(loop) -> None:
    for message in valid_data:
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


@server_running_required
def test_server_with_wrong_data(loop) -> None:
    for message in wrong_data:
        async_client = AsyncClient(
            HOST,
            PORT,
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


def test_request_manager_with_valid_request(loop):
    # TODO add test database
    request = "print_all_users"
    req_man = RequestManager(DSN)
    response = loop.run_until_complete(req_man.entrypoint(request))
    # TODO add assertion
    print("response:", response)
    assert type(response) == dict


def test_request_manager_with_unknown_request(loop):
    request = "unknown_request"
    req_man = RequestManager(DSN)
    response = loop.run_until_complete(req_man.entrypoint(request))
    assert response == {"answer": "Unknown request"}
