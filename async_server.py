""" Implementation of the server. """

from typing import *

import asyncio

from message_stream import MessageStream
from request_manager import RequestManager
from settings import DATABASES


class AsyncServer:
    def __init__(
        self,
        host: str,
        port: int,
        loop: asyncio.AbstractEventLoop = None,
        db_config: Dict = DATABASES["default"],
    ):
        self.host = host
        self.port = port
        self.req_man = RequestManager(db_config=db_config)
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop

    async def start_server(self) -> asyncio.AbstractServer:
        server = await asyncio.start_server(
            self.handle_connection, self.host, self.port
        )
        addr = self.get_addr(server)
        print(f"Serving on {addr}")
        return server

    @staticmethod
    def get_addr(server: asyncio.AbstractServer) -> str:
        return server.sockets[0].getsockname() if server.sockets else "unknown"

    async def handle_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        addr = writer.get_extra_info("peername")
        message = MessageStream(reader, writer)
        try:
            header, request = await message.receive_stream()
        except (ConnectionResetError, ValueError) as e:
            print(f"An error occurred: {e} when address: {addr} connect.")
        else:
            response = await self.get_answer_from_db(request)
            await message.send_stream(response, "json", "utf-8")
        finally:
            message.close()

    async def get_answer_from_db(self, request: Union[str, Dict, bytes]) -> Dict:
        return await self.req_man.entrypoint(request)

    def run_server(self) -> asyncio.AbstractServer:
        server = self.loop.run_until_complete(self.start_server())
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        return server

    def close(self, server: asyncio.AbstractServer) -> None:
        server.close()
        self.loop.run_until_complete(server.wait_closed())
        self.loop.close()
