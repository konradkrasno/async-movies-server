from typing import *

import asyncio

from message_stream import MessageStream


class AsyncClient:

    def __init__(self, host: str, port: int, loop: asyncio.AbstractEventLoop = None, test_message: str = ''):
        self.host = host
        self.port = port
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop
        self.test_message = test_message
        self.message = MessageStream()

    async def send_request(self, test_message: str = '') -> str:
        # TODO refactor this function

        encoding = "utf-8"
        reader, writer = await asyncio.open_connection(self.host, self.port)

        if test_message:
            message = test_message
        else:
            message = input()
        print(message)

        # sending message
        await self.message.send_data(writer, message, encoding)

        answer = await self.message.stream_receive(reader)

        print("Close the socket")
        writer.close()

        return answer['data']

    def run_client(self) -> str:
        return self.loop.run_until_complete(self.send_request(test_message=self.test_message))

    def close(self):
        self.loop.close()
