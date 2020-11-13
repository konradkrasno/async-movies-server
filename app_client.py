import sys

from async_client import AsyncClient
from app_server import HOST, PORT


if __name__ == "__main__":
    test_message = "get_all_data"
    async_client = AsyncClient(
        HOST,
        PORT,
        test_request=test_message,
        test_content_type="text",
    )
    async_client.run_client()
    async_client.close()
