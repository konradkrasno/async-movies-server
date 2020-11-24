""" Provides classes for creating, managing, and dropping test database and movies-database. """

from typing import *

from sqlalchemy.engine import Engine, Connection
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.pool import NullPool
import logging
import datetime

from settings import DATABASES
import models

logging.basicConfig(level=logging.DEBUG)


class Config:
    """ Provides configuration data for connecting to the database. """

    dsn_format = "postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}"

    def __init__(self, db_config: Dict):
        self.dsn_default = self.dsn_format.format(**db_config)

    @property
    def default_db_engine(self) -> Engine:
        return create_engine(self.dsn_default)


class TempDB(Config):
    """ Creates the database for testing purposes. """

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
    def test_db_engine(self) -> Engine:
        return create_engine(self.dsn_test, poolclass=NullPool)

    def setup_module(self) -> None:
        with self.default_db_engine.connect() as conn:
            conn.execute("COMMIT")
            logging.info(f" {datetime.datetime.now()}: Creating test database.")
            self.create_db(conn)

    @staticmethod
    def create_db(conn: Connection) -> None:
        try:
            conn.execute("CREATE DATABASE %s" % DATABASES["test"]["NAME"])
        except ProgrammingError:
            logging.error("Database '%s' already exists." % DATABASES["test"]["NAME"])

    def create_tables(self) -> None:
        with self.test_db_engine.connect() as conn:
            logging.info(f" {datetime.datetime.now()}: Creating tables.")
            models.Base.metadata.create_all(conn)

    def teardown_module(self) -> None:
        with self.default_db_engine.connect() as conn:
            conn.execute("COMMIT")
            logging.info(f" {datetime.datetime.now()}: Dropping test database.")
            self.drop_db(conn)

    @staticmethod
    def drop_db(conn: Connection) -> None:
        try:
            conn.execute("DROP DATABASE %s" % DATABASES["test"]["NAME"])
        except ProgrammingError:
            logging.error("Database '%s' does not exist." % DATABASES["test"]["NAME"])


class DBManager(Config):
    """ Handles managing access to the database. """

    def __init__(self, db_config: Dict = DATABASES["default"]):
        super().__init__(db_config)

    def create_tables(self) -> None:
        with self.default_db_engine.connect() as conn:
            logging.info(f" {datetime.datetime.now()}: Creating tables.")
            models.Base.metadata.create_all(conn)

    # def get_all_data(self) -> None:
    #     session = sessionmaker(bind=self.default_db_engine)()
    #     print("All data:")
    #     for instance in session.query(models.Genre).order_by(models.Genre.id):
    #         print(instance.id, instance.name)
    #
    #     for instance in session.query(models.MovieMetadata).order_by(models.MovieMetadata.id):
    #         print(instance.id, instance.title, instance.genres)
