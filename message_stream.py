from typing import *

import asyncio


class MessageStream:

    def __init__(self):
        self.encoding = None

    async def stream_receive(self, reader: asyncio.StreamReader) -> Dict[str, str]:
        # TODO refactor this function
        encoding = 'utf-8'
        buffer = f""
        message_length = 0
        print(f"Received: ", end="")
        while True:
            data = await reader.read(10)
            print(data.decode())
            await asyncio.sleep(0.25)
            buffer += data.decode()
            if "|" in buffer:
                message_length, buffer = buffer.split("|")
            if len(buffer) == int(message_length):
                break
        message = {
            'data': buffer,
            'encoding': encoding
        }
        return message

    async def send_data(self, writer: asyncio.StreamWriter, message: str, encoding: str) -> None:
        print(f"Sending: {message}")
        message = self.add_header(message)
        writer.write(message.encode(encoding=encoding))

    def add_header(self, message: str) -> str:
        # TODO refactor
        return str(len(message)) + "|" + message
