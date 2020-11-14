import sys

from async_server import AsyncServer
from settings import SERVER


if __name__ == "__main__":
    async_server = AsyncServer(SERVER["HOST"], SERVER["PORT"])
    server = async_server.run_server()
    async_server.close(server)
