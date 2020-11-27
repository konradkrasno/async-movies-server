""" Creates and connects the client with the server. """

import sys

from async_client import AsyncClient

HOST = "127.0.0.1"
PORT = 12345


if __name__ == "__main__":
    async_client = AsyncClient(HOST, PORT)
    for message in sys.stdin:
        header, answer = async_client.run_client(
            request=message, content_type="text", encoding="utf-8"
        )
        print("header:", header)
        print("answer:", answer)
    async_client.close()
