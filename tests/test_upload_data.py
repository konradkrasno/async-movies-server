""" Provides tests for upload_data_to_db module. """

from typing import *

import pytest
import numpy as np

import models
from upload_data import (
    upload_csv,
    upload_movies_metadata,
    upload_movies_credits,
    upload_movies_keywords,
    upload_data_to_db,
    load_to_json,
)
from handle_sessions import HandleSession, open_session
from tests.db_fixtures import TestDB


class TestUploadData(TestDB):

    @pytest.fixture
    def data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return upload_csv("archive/test")

    @staticmethod
    def test_load_to_json(data):
        row = data[1][0]
        assert load_to_json(row[0])
        assert load_to_json(row[1])

    def test_upload_movies_metadata(self, data):
        engine = self.temp_db.test_db_engine
        row = data[0][0]
        open_session(engine, upload_movies_metadata, row)
        with HandleSession(engine) as handle:
            assert handle.session.query(models.Genre).all()
            assert handle.session.query(models.ProductionCompany).all()
            assert handle.session.query(models.Country).all()
            assert handle.session.query(models.Language).all()
            assert handle.session.query(models.MovieMetadata).all()

    def test_upload_movies_credits(self, data):
        engine = self.temp_db.test_db_engine
        movie_metadata = data[0][0]
        open_session(engine, upload_movies_metadata, movie_metadata)
        credits_data = data[1][0]
        open_session(engine, upload_movies_credits, credits_data)
        with HandleSession(engine) as handle:
            assert handle.session.query(models.Actor).all()
            assert handle.session.query(models.CrewMember).all()
            assert handle.session.query(models.Character).all()
            assert handle.session.query(models.Crew).all()

    def test_upload_movies_keywords(self, data):
        engine = self.temp_db.test_db_engine
        movie_metadata = data[0][0]
        open_session(engine, upload_movies_metadata, movie_metadata)
        keywords_data = data[2][0]
        open_session(engine, upload_movies_keywords, keywords_data)
        with HandleSession(engine) as handle:
            assert handle.session.query(models.Keywords).all()

    def test_upload_data(self, data):
        engine = self.temp_db.test_db_engine
        open_session(engine, upload_data_to_db, data)
        with HandleSession(engine) as handle:
            assert handle.session.query(models.MovieMetadata).all()
            assert handle.session.query(models.Character).all()
            assert handle.session.query(models.Crew).all()
            assert handle.session.query(models.Keywords).all()
