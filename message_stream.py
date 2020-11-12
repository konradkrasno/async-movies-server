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
        self.data_to_send: bytes = b""
        self.content_to_send: bytes = b""
        self.content_type_to_send: str = ""
        self.header_to_send: Dict[str, Union[str, int]] = {}
        self.header_len_to_send: int = int()
        self.encoding_to_send: str = "utf-8"

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
        else:
            self.recv_content = "Unknown received content type."

    async def send_stream(
        self,
        writer: asyncio.StreamWriter,
        data: Union[str, Dict, bytes],
        content_type: str,
        encoding: str = "utf-8",
    ) -> None:
        self.validate_input(writer, data, content_type, encoding)
        self.prepare_data_to_send()
        print(f"Sending: {self.content_to_send}")
        writer.write(self.data_to_send)
        await writer.drain()

    def validate_input(self, writer: asyncio.StreamWriter, data: Union[str, Dict, bytes], content_type: str, encoding: str) -> None:
        if encoding not in ("utf-8", "ascii"):
            writer.close()
            raise ValueError("Wrong encoding! Available encodings: utf-8, ascii.")
        self.encoding_to_send = encoding

        if type(data) in (dict, json) and content_type == "json":
            self.content_to_send = self.encode_json(data)
        elif type(data) == str and content_type == "text":
            self.content_to_send = data.encode(self.encoding_to_send)
        elif type(data) == bytes and content_type == "binary":
            self.content_to_send = data
        else:
            writer.close()
            raise ValueError(f"Wrong value of data: {data} or content_type: {content_type}.")
        self.content_type_to_send = content_type

    def prepare_data_to_send(self) -> None:
        self.create_header_to_send()
        self.get_header_len_to_send()
        self.merge_data_to_send()

    def create_header_to_send(self) -> None:
        self.header_to_send = {
            "content_type": self.content_type_to_send,
            "content_encoding": self.encoding_to_send,
            "content_length": len(self.content_to_send),
        }

    def get_header_len_to_send(self) -> None:
        self.header_len_to_send = len(self.encode_json(self.header_to_send))

    def merge_data_to_send(self) -> None:
        self.data_to_send = (
            self.encode_header_len_to_send()
            + self.encode_json(self.header_to_send)
            + self.content_to_send
        )

    def encode_header_len_to_send(self) -> bytes:
        return struct.pack(">H", self.header_len_to_send)

    @staticmethod
    def decode_json(obj: bytes) -> json:
        return json.loads(obj)

    def encode_json(self, data: Dict) -> bytes:
        return json.dumps(data).encode(self.encoding_to_send)
