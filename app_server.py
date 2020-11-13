import sys

from async_server import AsyncServer
import json

HOST = "172.17.0.3"
PORT = 12345
with open("secure.json", "r") as file:
    secure = json.load(file)
DSN = f'postgres://postgres:{secure["PG_PASSWORD"]}@172.17.0.2/postgres'


if __name__ == "__main__":
    async_server = AsyncServer(HOST, PORT, DSN)
    server = async_server.run_server()
    async_server.close(server)
