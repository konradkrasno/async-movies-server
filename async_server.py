from typing import *

import asyncio

from message_stream import MessageStream


class AsyncServer:
    def __init__(self, host: str, port: int, loop: asyncio.AbstractEventLoop = None):
        self.host = host
        self.port = port
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
        ctx = {"addr": writer.get_extra_info("peername")}
        message = MessageStream(response_content_type="text", response_encoding="utf-8")
        request = await message.receive_stream(reader)
        await message.send_data(writer, request)
        print("Close the client socket")
        writer.close()

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
