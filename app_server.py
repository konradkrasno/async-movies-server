import sys

from async_server import AsyncServer

HOST = "127.0.0.1"
PORT = 12345


if __name__ == "__main__":
    async_server = AsyncServer(HOST, PORT)
    server = async_server.run_server()
    async_server.close(server)
