""" Provides tests for db_manager module. """

import pytest

from db_manager import DBManager, TempDB
from settings import DATABASES


class TestDB:
    temp_db = TempDB()

    @classmethod
    def setup_class(cls):
        cls.temp_db.setup_module()
        cls.temp_db.create_tables()

    @classmethod
    def teardown_class(cls):
        cls.temp_db.teardown_module()


@pytest.fixture
def db_manager() -> DBManager:
    db_manager = DBManager(db_config=DATABASES["test"])
    return db_manager
