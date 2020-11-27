""" Handles requests to the database. """

from typing import *

import asyncpg

from settings import DATABASES


class RequestManager:
    dsn_format = "postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}"

    def __init__(self, db_config: Dict = DATABASES["docker"]):
        self.dsn = self.dsn_format.format(**db_config)
        self.encoding = "utf-8"

    async def entrypoint(self, request: Any) -> Dict:
        """ Processes the request message to get information from it and creates the database pool. """

        request = self.process_request(request)
        async with asyncpg.create_pool(self.dsn) as db:
            return await self.handle_request(db, request)

    @classmethod
    def process_request(cls, request: Any) -> Dict:
        """ Gets information from the request. """

        if type(request) == str:
            request = cls.clean_query(request)
            try:
                category, query = request.split(", ")
            except ValueError:
                return {
                    "category": "wrong_request",
                }
            else:
                request = {
                    "category": category,
                    "query": query,
                }
            return request
        elif type(request) == dict:
            return request
        else:
            return {
                "category": "wrong_type",
            }

    async def handle_request(self, db: asyncpg.pool.Pool, request: Dict) -> Dict:
        """ Manages the requests. If the request is proper, queries the database. """

        category = request.get("category")
        query = request.get("query")
        try:
            query = self.query_manager[category](query)
        except KeyError:
            answer = "The request can not be processed."
        else:
            if category in ["wrong_type", "wrong_request"]:
                answer = query
            else:
                answer = await self.query_db(db, query)
        return self.give_response(answer)

    @property
    def query_manager(self) -> Dict[str, Callable]:
        return {
            "title": self.get_by_title,
            "actor": self.get_by_actor,
            "director": self.get_by_director,
            "screenplay": self.get_by_screenplay,
            "custom": self.custom_query,
            "wrong_request": self.wrong_request,
            "wrong_type": self.wrong_type,
        }

    @staticmethod
    def get_by_title(title: str) -> str:
        return """
        SELECT * FROM movies_metadata movies
        WHERE movies.title = '%s'
        """ % (
            title,
        )

    @staticmethod
    def get_by_actor(actor: str) -> str:
        return """
        SELECT title FROM movies_metadata movies
        INNER JOIN characters ON characters.movie_id = movies.id
        INNER JOIN actors ON actors.id = characters.actor_id
        WHERE actors.name = '%s';
        """ % (
            actor,
        )

    @staticmethod
    def get_by_director(director: str) -> str:
        return """
        SELECT title FROM movies_metadata movies
        INNER JOIN crew ON crew.movie_id = movies.id
        INNER JOIN crew_members ON crew_members.id = crew.crew_member_id
        WHERE crew.job = 'Director'
        AND crew_members.name = '%s';
        """ % (
            director,
        )

    @staticmethod
    def get_by_screenplay(screenplay: str) -> str:
        return """
        SELECT title FROM movies_metadata movies
        INNER JOIN crew ON crew.movie_id = movies.id
        INNER JOIN crew_members ON crew_members.id = crew.crew_member_id
        WHERE crew.department = 'Writing'
        AND crew_members.name = '%s';
        """ % (
            screenplay,
        )

    @classmethod
    def custom_query(cls, query: str) -> str:
        return cls.clean_query(query)

    @staticmethod
    def wrong_request(*args) -> str:
        return "Wrong request content."

    @staticmethod
    def wrong_type(*args) -> str:
        return "Wrong request type. Required type: text or JSON."

    @staticmethod
    def clean_query(query: str) -> str:
        query = query.replace("\n", "")
        return query

    @classmethod
    async def query_db(cls, db: asyncpg.pool.Pool, query: str) -> list:
        records = list()
        async with db.acquire() as conn:
            async with conn.transaction():
                async for record in conn.cursor(query):
                    record = cls.process_record(record)
                    records.append(record)
        return records

    @staticmethod
    def process_record(record: asyncpg.Record) -> Dict:
        record = {**record}
        try:
            release_date = record["release_date"]
        except KeyError:
            pass
        else:
            record["release_date"] = release_date.strftime("%d-%b-%Y")
        return record

    @staticmethod
    def give_response(answer: Union[str, List, Dict]) -> Dict:
        return {
            "answer": answer,
        }
