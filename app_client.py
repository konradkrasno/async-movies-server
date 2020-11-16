""" Creates and connects the client with the server,
    after that it sends the specified request to the server. """

import sys

from async_client import AsyncClient

HOST = "172.17.0.2"
PORT = 12345


if __name__ == "__main__":
    test_message = "get_all_data"
    async_client = AsyncClient(
        HOST, PORT, test_request=test_message, test_content_type="text"
    )
    async_client.run_client()
    async_client.close()
