from typing import *

import asyncio
import json
import struct


class MessageStream:
    def __init__(self):
        self.recv_buffer: bytes = b""
        self.recv_content: Union[str, Dict, bytes] = {}
        self.recv_header: Dict[str, Union[str, int]] = {}
        self.recv_header_len: int = int()
        self.send_data: bytes = b""
        self.send_content: bytes = b""
        self.send_content_type: str = ""
        self.send_header: Dict[str, Union[str, int]] = {}
        self.send_header_len: int = int()
        self.send_encoding: Union[str, None] = None

    async def receive_stream(
        self, reader: asyncio.StreamReader
    ) -> Tuple[Dict, Union[str, Dict, bytes]]:
        if not self.recv_header_len:
            await self.get_recv_header_len(reader)
        await self.get_recv_header(reader)
        await self.get_recv_content(reader)
        return self.recv_header, self.recv_content

    async def get_recv_header_len(self, reader: asyncio.StreamReader) -> None:
        data = await reader.read(2)
        if data:
            self.recv_header_len = struct.unpack(">H", data)[0]

    async def get_recv_header(self, reader: asyncio.StreamReader) -> None:
        if self.recv_header_len <= 0:
            raise ValueError("Header length must be greater than 0!")

        while True:
            if len(self.recv_buffer) >= self.recv_header_len:
                break
            data = await reader.read(10)
            # Simulate network latency
            await asyncio.sleep(0.1)
            print(data.decode())
            self.recv_buffer += data
        header = self.recv_buffer[: self.recv_header_len]
        self.recv_header = self.decode_json(header)
        self.recv_buffer = self.recv_buffer[self.recv_header_len:]

    async def get_recv_content(self, reader: asyncio.StreamReader) -> None:
        content_len = self.recv_header["content_length"]
        while True:
            if len(self.recv_buffer) >= content_len:
                break
            data = await reader.read(10)
            # Simulate network latency
            await asyncio.sleep(0.1)
            print(data.decode())
            self.recv_buffer += data
        self.decode_recv_content()
        self.recv_buffer = self.recv_buffer[content_len:]

    def decode_recv_content(self) -> None:
        content_type = self.recv_header["content_type"]
        if content_type == "text":
            self.recv_content = self.recv_buffer.decode()
        elif content_type == "json":
            self.recv_content = self.decode_json(self.recv_buffer)
        elif content_type == "binary":
            self.recv_content = self.recv_buffer

    async def send_stream(
        self,
        writer: asyncio.StreamWriter,
        data: Union[str, Dict, bytes],
        content_type: str,
        encoding: Union[str, None],
    ) -> None:
        self.send_content_type = content_type
        self.send_encoding = encoding
        self.add_send_content(data)
        self.prepare_send_data()
        writer.write(self.send_data)
        await writer.drain()

    def add_send_content(self, data: Union[str, Dict, bytes]) -> None:
        if self.send_content_type == "text":
            self.send_content = data.encode(self.send_encoding)
        elif self.send_content_type == "json":
            self.send_content = self.encode_json(data)
        elif self.send_content_type == "binary":
            self.send_content = data

    def prepare_send_data(self) -> None:
        self.create_send_header()
        self.get_send_header_len()
        self.merge_send_data()

    def create_send_header(self) -> None:
        self.send_header = {
            "content_type": self.send_content_type,
            "content_encoding": self.send_encoding,
            "content_length": len(self.send_content),
        }

    def get_send_header_len(self) -> None:
        self.send_header_len = len(self.encode_json(self.send_header))

    def merge_send_data(self) -> None:
        self.send_data = (
            self.encode_send_header_len()
            + self.encode_json(self.send_header)
            + self.send_content
        )

    def encode_send_header_len(self) -> bytes:
        return struct.pack(">H", self.send_header_len)

    @staticmethod
    def decode_json(obj: bytes) -> json:
        return json.loads(obj)

    def encode_json(self, data: Dict) -> bytes:
        return json.dumps(data).encode(self.send_encoding)
