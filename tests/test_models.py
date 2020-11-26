""" Provides tests for models module. """

import pytest

import models
from handle_sessions import HandleSession
from tests.db_fixtures import temp_db


@pytest.mark.parametrize(
    "model, data, checking_attrs",
    [
        (models.Genre, [{"name": "US"}, {"name": "US"}], ["name"]),
        (
            models.ProductionCompany,
            [{"name": "Warner Bros"}, {"name": "Warner Bros"}],
            ["name"],
        ),
        (
            models.Country,
            [
                {"iso_3166_1": "iso-1", "name": "US"},
                {"iso_3166_1": "iso-1", "name": "Poland"},
                {"iso_3166_1": "iso-2", "name": "US"},
            ],
            ["iso_3166_1", "name"],
        ),
        (
            models.Language,
            [
                {"iso_639_1": "iso-5", "name": "English"},
                {"iso_639_1": "iso-5", "name": "Polish"},
                {"iso_639_1": "iso-10", "name": "English"},
            ],
            ["iso_639_1", "name"],
        ),
        (
            models.Actor,
            [
                {
                    "id": 1,
                    "name": "test",
                    "gender": 2,
                    "profile_path": "example/path",
                },
            ],
            ["id"],
        ),
        (
            models.CrewMember,
            [
                {
                    "id": 5,
                    "name": "test",
                    "gender": 1,
                    "profile_path": "example/path",
                },
            ],
            ["id"],
        ),
    ],
)
def test_get_or_create(temp_db, model, data, checking_attrs):
    engine = temp_db.test_db_engine
    with HandleSession(engine) as handle:
        for attr in checking_attrs:
            assert not (
                handle.session.query(model)
                .filter(model.__getattribute__(model, attr) == data[0][attr])
                .first()
            )
    with HandleSession(engine) as handle:
        for item in data:
            record = model.get_or_create(handle.session, **item)
            handle.session.add(record)
            handle.session.commit()
    with HandleSession(engine) as handle:
        for attr in checking_attrs:
            assert (
                handle.session.query(model)
                .filter(model.__getattribute__(model, attr) == data[0][attr])
                .first()
            )
