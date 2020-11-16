""" Provides tests for db_manager module. """

import pytest

from db_manager import DBManager, TempDB, HandleSession
from settings import DATABASES

import models


class TestDBManager:
    @pytest.fixture()
    def temp_db(self):
        temp_db = TempDB()
        temp_db.setup_module()
        temp_db.create_tables()
        try:
            yield temp_db
        finally:
            temp_db.teardown_module()

    @pytest.fixture
    def db_manager(self) -> DBManager:
        db_manager = DBManager(db_config=DATABASES["test"])
        return db_manager

    def test_add_record(self, temp_db, db_manager) -> None:
        db_manager.add_record(models.Genre, name="drama")
        with HandleSession(db_manager.engine_default) as handle:
            assert (
                handle.session.query(models.Genre)
                .filter(models.Genre.name == "drama")
                .first()
            )

    def test_add_movie_metadata(self, temp_db, db_manager) -> None:
        db_manager.add_movie_metadata(1, "drama", "thriller")
        with HandleSession(db_manager.engine_default) as handle:
            assert (
                handle.session.query(models.MovieMetadata)
                .filter(models.MovieMetadata.title == "Example movie")
                .first()
            )
            assert (
                handle.session.query(models.Genre)
                .filter(models.Genre.name == "drama")
                .first()
            )
            assert (
                handle.session.query(models.Genre)
                .filter(models.Genre.name == "thriller")
                .first()
            )
            assert not (
                handle.session.query(models.Genre)
                .filter(models.Genre.name == "comedy")
                .first()
            )
