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

    @staticmethod
    async def handle_connection(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        addr = writer.get_extra_info("peername")
        message = MessageStream(reader, writer)
        try:
            header, request = await message.receive_stream()
        except (ConnectionResetError, ValueError) as e:
            print(f"An error occurred: {e} when address: {addr} connect.")
        else:
            await message.send_stream(
                request, header["content_type"], header["content_encoding"]
            )
        finally:
            message.close()

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
