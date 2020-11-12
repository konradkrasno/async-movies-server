import sys

from async_client import AsyncClient

HOST = "127.0.0.1"
PORT = 12345


if __name__ == "__main__":
    test_message = {
        "name": "Jim",
        "message": "Well, I'm the crawlin' king snake And I rule my den I'm the crawlin' king snake And I rule my den",
    }
    async_client = AsyncClient(
        HOST,
        PORT,
        test_request=test_message,
        test_content_type="json",
    )
    async_client.run_client()
    async_client.close()
