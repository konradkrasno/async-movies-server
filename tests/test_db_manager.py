import pytest

from db_manager import DBManager, temp_db, HandleSession
from settings import DATABASES

import models


# @pytest.mark.temp_db
class TestDBManager:
    # # TODO add custom mark with temp_db
    # pytestmark = pytest.mark.temp_db

    @pytest.fixture
    def db_manager(self) -> DBManager:
        db_manager = DBManager(db_config=DATABASES["test"])
        return db_manager

    # @temp_db
    # def test_add_record(self, db_manager) -> None:
    #     db_manager.add_record(models.Genre, name="drama")
    #     with HandleSession(db_manager.engine_default) as handle:
    #         assert handle.session.query(models.Genre).filter(models.Genre.name == "drama").first()

    @temp_db
    def test_add_movie_metadata(self, db_manager) -> None:
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
