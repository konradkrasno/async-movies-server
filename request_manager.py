from typing import *

import asyncpg
import asyncio
import json

with open("secure.json", "r") as file:
    secure = json.load(file)


class RequestManager:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.encoding = 'utf-8'

    @property
    def request_manager(self) -> Dict[str, Callable]:
        manager = {
            "get_all_data": self.print_all_users,
            "wrong_type": self.handle_wrong_type,
        }
        return manager

    @staticmethod
    async def print_all_users(db: asyncpg.pool.Pool) -> list:
        records = list()
        async with db.acquire() as conn:
            async with conn.transaction():
                async for record in conn.cursor("SELECT * FROM users;"):
                    records.append({**record})
        return records

    @staticmethod
    async def handle_wrong_type(db: asyncpg.pool.Pool) -> str:
        return "Wrong request type. Required type: text."

    async def entrypoint(self, request: Any) -> Dict:
        request = self.process_request(request)
        async with asyncpg.create_pool(
            self.dsn, password=secure["PG_PASSWORD"]
        ) as db:
            return await self.handle_request(db, request)

    @staticmethod
    def process_request(request: Any) -> str:
        if type(request) == str:
            return request
        else:
            return "wrong_type"

    async def handle_request(self, db: asyncpg.pool.Pool, request: str) -> Dict:
        try:
            answer = await self.request_manager[request](db)
        except KeyError:
            answer = "Unknown request"
        return self.give_response(answer)

    @staticmethod
    def give_response(answer: Union[str, List, Dict]) -> Dict:
        return {
            "answer": answer,
        }