""" Provides tests for db_manager module. """

import pytest

from db_manager import DBManager, TempDB
from settings import DATABASES


@pytest.fixture()
def temp_db():
    temp_db = TempDB()
    temp_db.setup_module()
    temp_db.create_tables()
    try:
        yield temp_db
    finally:
        temp_db.teardown_module()


@pytest.fixture
def db_manager() -> DBManager:
    db_manager = DBManager(db_config=DATABASES["test"])
    return db_manager
