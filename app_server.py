""" Creates and starts running the server. """

from async_server import AsyncServer
from settings import SERVER, DATABASES


if __name__ == "__main__":
    async_server = AsyncServer(
        SERVER["HOST"], SERVER["PORT"], db_config=DATABASES["default"]
    )
    server = async_server.run_server()
    async_server.close(server)
