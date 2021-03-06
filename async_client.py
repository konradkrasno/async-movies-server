""" Implementation of the client. """

from typing import *

import asyncio

from message_stream import MessageStream


class AsyncClient:
    """ Initializes and manages the client. """

    def __init__(
        self,
        host: str,
        port: int,
        loop: asyncio.AbstractEventLoop = None,
    ):
        self.host = host
        self.port = port
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop
        # Call print_instruction function
        self.print_instruction()

    @staticmethod
    def print_instruction() -> None:
        print(
            """Enter one of the phrases to download data from the server: 
            title, 'specify title'
            actor, 'specify actor'
            director, 'specify director'
            screenplay, 'specify screenplay'
            custom, 'custom query'"""
        )

    def run_client(
        self, request: Union[str, bytes, Dict], content_type: str, encoding: str
    ) -> Tuple[Dict, Union[str, Dict, bytes]]:
        """ Runs the event loop. """
        return self.loop.run_until_complete(
            self.handle_connection(request, content_type, encoding)
        )

    async def handle_connection(
        self, request: Union[str, bytes, Dict], content_type: str, encoding: str
    ) -> Tuple[Dict, Union[str, Dict, bytes]]:
        """ Sends the request to the server and receives data from it. """

        reader, writer = await asyncio.open_connection(self.host, self.port)
        message = MessageStream(reader, writer)
        await message.send_stream(request, content_type, encoding)
        try:
            header, answer = await message.receive_stream()
        except ValueError:
            print(f"An error occurred when receiving data from server.")
        else:
            return header, answer
        finally:
            message.close()
        return dict(), str()

    def close(self) -> None:
        """ Closing the event loop. """
        self.loop.close()
