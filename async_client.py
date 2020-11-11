from typing import *

import asyncio

from message_stream import MessageStream


class AsyncClient:
    def __init__(
        self,
        host: str,
        port: int,
        loop: asyncio.AbstractEventLoop = None,
        test_data: str = "",
    ):
        self.host = host
        self.port = port
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop
        self._test_data = test_data

    async def send_request(self) -> str:
        reader, writer = await asyncio.open_connection(self.host, self.port)

        if self._test_data:
            data = self._test_data
        else:
            data = input()
        print(f"Sending: {data}")

        message = MessageStream(response_content_type="text", response_encoding="utf-8")
        await message.send_data(writer, data)
        answer = await message.receive_stream(reader)
        print("answer:", answer)
        print("Close the socket")
        writer.close()
        return answer

    def run_client(self) -> str:
        return self.loop.run_until_complete(self.send_request())

    def close(self) -> None:
        self.loop.close()
