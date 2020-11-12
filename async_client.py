from typing import *

import asyncio

from message_stream import MessageStream


class AsyncClient:
    def __init__(
        self,
        host: str,
        port: int,
        loop: asyncio.AbstractEventLoop = None,
        test_request: Union[str, Dict, bytes] = None,
        test_content_type: str = "",
        test_encoding: str = "",
    ):
        self.host = host
        self.port = port
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop
        self._test_request = test_request
        self._test_content_type = test_content_type
        self._test_encoding = test_encoding

    async def send_request(self) -> Tuple[Dict, Union[str, Dict, bytes]]:
        reader, writer = await asyncio.open_connection(self.host, self.port)

        if self._test_request:
            request = self._test_request
        else:
            request = input()
        if self._test_content_type:
            content_type = self._test_content_type
        else:
            content_type = "text"
        if self._test_encoding:
            encoding = self._test_encoding
        else:
            encoding = "utf-8"

        message = MessageStream()
        await message.send_stream(writer, request, content_type, encoding)
        header, answer = await message.receive_stream(reader)
        print("header:", header)
        print("answer:", answer)
        print("Close the socket")
        writer.close()
        return header, answer

    def run_client(self) -> Tuple[Dict, Union[str, Dict, bytes]]:
        return self.loop.run_until_complete(self.send_request())

    def close(self) -> None:
        self.loop.close()
