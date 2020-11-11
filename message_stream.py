from typing import *

import asyncio
import json
import struct


class MessageStream:
    def __init__(self, response_content_type: str, response_encoding: str):
        self.request_buffer: bytes = b""
        self.request_content: Union[str, Dict, bytes] = {}
        self.request_header: Dict[str, Union[str, int]] = {}
        self.request_header_len: int = int()

        self.response_data: bytes = b""
        self.response_content: bytes = b""
        self.response_content_type = response_content_type
        self.response_header: Dict[str, Union[str, int]] = {}
        self.response_header_len: int = int()
        self.response_encoding: str = response_encoding

    async def receive_stream(
        self, reader: asyncio.StreamReader
    ) -> Union[str, Dict, bytes]:
        if not self.request_header_len:
            await self.get_request_header_len(reader)
        await self.get_request_header(reader)
        await self.get_request_content(reader)
        return self.request_content

    async def get_request_header_len(self, reader: asyncio.StreamReader) -> None:
        data = await reader.read(2)
        if data:
            self.request_header_len = struct.unpack(">H", data)[0]

    async def get_request_header(self, reader: asyncio.StreamReader) -> None:
        # TODO add avoiding infinite loop when wrong header len
        while True:
            data = await reader.read(10)
            # Simulate network latency
            await asyncio.sleep(0.2)
            print(data.decode())
            self.request_buffer += data
            if len(self.request_buffer) >= self.request_header_len:
                break
        header = self.request_buffer[:self.request_header_len]
        self.request_header = self.decode_json(header)
        self.request_buffer = self.request_buffer[self.request_header_len:]

    async def get_request_content(self, reader: asyncio.StreamReader) -> None:
        # TODO add avoiding infinite loop when wrong content len
        content_len = self.request_header["content_length"]
        while True:
            data = await reader.read(10)
            # Simulate network latency
            await asyncio.sleep(0.2)
            print(data.decode())
            self.request_buffer += data
            if len(self.request_buffer) >= content_len:
                break
        self.decode_request_content()
        self.request_buffer = self.request_buffer[content_len:]

    def decode_request_content(self) -> None:
        content_type = self.request_header["content_type"]
        if content_type == "text":
            self.request_content = self.request_buffer.decode()
        elif content_type == "json":
            self.request_content = self.decode_json(self.request_buffer)
        elif content_type == "binary":
            self.request_content = self.request_buffer

    async def send_data(
        self, writer: asyncio.StreamWriter, data: Union[str, Dict, bytes]
    ) -> None:
        self.add_response_content(data)
        self.prepare_response()
        writer.write(self.response_data)
        await writer.drain()

    def add_response_content(self, data: Union[str, Dict, bytes]) -> None:
        if self.response_content_type == "text":
            self.response_content = data.encode(self.response_encoding)
        elif self.response_content_type == "json":
            self.response_content = self.encode_json(data)
        elif self.response_content_type == "binary":
            self.response_content = data

    def prepare_response(self) -> None:
        self.create_response_header()
        self.get_response_header_len()
        self.merge_response_data()

    def create_response_header(self) -> None:
        self.response_header = {
            "content_type": self.response_content_type,
            "content_encoding": self.response_encoding,
            "content_length": len(self.response_content),
        }

    def get_response_header_len(self) -> None:
        self.response_header_len = len(self.encode_json(self.response_header))

    def merge_response_data(self) -> None:
        self.response_data = (
            self.encode_response_header_len()
            + self.encode_json(self.response_header)
            + self.response_content
        )

    def encode_response_header_len(self) -> bytes:
        return struct.pack(">H", self.response_header_len)

    @staticmethod
    def decode_json(obj: bytes) -> json:
        return json.loads(obj)

    def encode_json(self, data: Dict) -> bytes:
        return json.dumps(data).encode(self.response_encoding)
