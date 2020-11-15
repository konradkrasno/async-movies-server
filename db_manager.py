from typing import *

from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError, IntegrityError, OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from functools import wraps

from settings import DATABASES

import sqlalchemy
import models
import logging

logging.basicConfig(level=logging.DEBUG)


class Config:
    dsn_format = "postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}"

    def __init__(self, db_config: Dict):
        self.dsn_default = self.dsn_format.format(**db_config)

    @property
    def engine_default(self) -> sqlalchemy.engine.Engine:
        return create_engine(self.dsn_default)


class TempDB(Config):
    """ Creates database for testing purposes. """

    def __init__(self):
        super().__init__(db_config=DATABASES["default"])
        self.dsn_test = self.dsn_format.format(**DATABASES["test"])

    def __enter__(self):
        self.setup_module()
        self.create_tables()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown_module()

    @property
    def engine_new(self) -> sqlalchemy.engine.Engine:
        return create_engine(self.dsn_test, poolclass=NullPool)

    def setup_module(self) -> None:
        with self.engine_default.connect() as conn:
            conn.execute("COMMIT")
            logging.info("Creating test database.")
            self.create_db(conn)

    @staticmethod
    def create_db(conn: sqlalchemy.engine.Connection) -> None:
        try:
            conn.execute("CREATE DATABASE %s" % DATABASES["test"]["NAME"])
        except ProgrammingError:
            logging.error("Database '%s' already exists." % DATABASES["test"]["NAME"])

    def create_tables(self) -> None:
        with self.engine_new.connect() as conn:
            logging.info("Creating tables.")
            models.Base.metadata.create_all(conn)

    def teardown_module(self) -> None:
        with self.engine_default.connect() as conn:
            conn.execute("COMMIT")
            logging.info("Dropping test database.")
            self.drop_db(conn)

    @staticmethod
    def drop_db(conn: sqlalchemy.engine.Connection) -> None:
        try:
            conn.execute("DROP DATABASE %s" % DATABASES["test"]["NAME"])
        except ProgrammingError:
            logging.error("Database '%s' does not exist." % DATABASES["test"]["NAME"])


def temp_db(func: callable) -> callable:
    """ Decorator for creating database for testing purpose. """

    @wraps(func)
    def wrapper(*args, **kwargs) -> None:
        with TempDB():
            func(*args, **kwargs)

    return wrapper


class HandleSession:
    """ Context manager for handling database sessions. """

    def __init__(self, engine: sqlalchemy.engine.Engine):
        self.engine = engine
        self.session = sessionmaker(bind=self.engine)()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        self.session.bind.dispose()


def open_session(engine: sqlalchemy.engine.Engine):
    """ Decorator for handling database sessions. """

    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with HandleSession(engine) as handle:
                for record in func(*args, **kwargs):
                    handle.session.add(record)
                    try:
                        handle.session.commit()
                    except IntegrityError:
                        pass

        return wrapper

    return inner


class DBManager(Config):
    def __init__(self, db_config: Dict = DATABASES["default"]):
        super().__init__(db_config)
        self.add_record = open_session(self.engine_default)(self.add_record)
        self.add_movie_metadata = open_session(self.engine_default)(
            self.add_movie_metadata
        )

    def create_tables(self) -> None:
        # TODO test it
        with self.engine_default.connect() as conn:
            logging.info("Creating tables.")
            models.Base.metadata.create_all(conn)

    @staticmethod
    def add_record(model: callable, **kwargs) -> Iterator:
        yield model(**kwargs)

    @staticmethod
    def add_movie_metadata(movie_id: int, *args: Any) -> Iterator:
        genres = list()
        for name in args:
            genre = models.Genre(name=name)
            genres.append(genre)
            yield genre

        yield models.MovieMetadata(
            id=movie_id,
            adult=True,
            budget=10000,
            genres=genres,
            homepage="http://example.com",
            original_language="English",
            original_title="Example",
            overview="Test text",
            popularity=8.5,
            poster_path="/path",
            release_date="15.12.1995",
            revenue=373554033,
            runtime=120,
            tagline="test text",
            title="Example movie",
            vote_average=7.34,
            vote_count=1000,
        )

    # def get_all_data(self) -> None:
    #     session = sessionmaker(bind=self.engine_default)()
    #     print("All data:")
    #     for instance in session.query(models.Genre).order_by(models.Genre.id):
    #         print(instance.id, instance.name)
    #
    #     for instance in session.query(models.MovieMetadata).order_by(models.MovieMetadata.id):
    #         print(instance.id, instance.title, instance.genres)
    #
    # def del_all_data_from_table(self, model) -> None:
    #     session = sessionmaker(bind=self.engine_default)()
    #     for instance in session.query(model).order_by(model.id):
    #         session.delete(instance)
    #     session.commit()
