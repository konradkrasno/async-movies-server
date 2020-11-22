""" Uploads data from csv files to the database. """

from typing import *

import pandas as pd
import numpy as np
import re
import json

import models

from sqlalchemy.orm import Session
from handle_sessions import open_session
from db_manager import DBManager
from settings import BASE_DIR
from itertools import zip_longest


def make_convertible_to_json(string: str) -> str:
    """ Processes input string to convertible to JSON. """

    keys = re.findall(r"(')(\w{1,10})(':)", string)
    for key in keys:
        string = string.replace("'{}'".format(key[1]), '"{}"'.format(key[1]))
    string = re.sub("\\'", '"', string)
    string = re.sub(r'(\w+)"(\w+)', r"\1\2", string)
    string = string.replace("None", '""')
    return string


def load_to_json(string: str) -> Dict:
    """ Converts string to JSON and returns. If an error occurred, returns empty Dict. """

    string = make_convertible_to_json(string)
    try:
        result = json.loads(string)
    except json.decoder.JSONDecodeError:
        return dict()
    return result


def upload_csv() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """ Reads data from csv files. """

    movies_metadata = pd.read_csv(
        BASE_DIR / "archive/movies_metadata.csv", low_memory=False
    )
    movies_credits = pd.read_csv(BASE_DIR / "archive/credits.csv")
    movies_keywords = pd.read_csv(BASE_DIR / "archive/keywords.csv")

    return movies_metadata.values, movies_credits.values, movies_keywords.values


def validate_adult(row: np.ndarray) -> np.ndarray:
    """ Converts the 'adult' variable to bool if it is a str. """

    adult = row[0]
    if adult == "False":
        adult = False
    elif adult == "True":
        adult = True
    row[0] = adult
    return row


def validate_runtime(row: np.ndarray) -> np.ndarray:
    """ Checks if the 'runtime' variable is int. When not, changes it to 0. """

    try:
        row[16] = int(row[16])
    except ValueError:
        row[16] = 0
    return row


def handle_related_models(
    row: np.ndarray,
) -> Dict[str, Dict[str, Union[Callable, List, Dict]]]:
    """ Matches appropriate columns from the row to models related to MovieMetadata. """

    return {
        "genres": {
            "model": models.Genre,
            "clipboard": list(),
            "data": load_to_json(row[3]),
        },
        "companies": {
            "model": models.ProductionCompany,
            "clipboard": list(),
            "data": load_to_json(row[12]),
        },
        "countries": {
            "model": models.Country,
            "clipboard": list(),
            "data": load_to_json(row[13]),
        },
        "languages": {
            "model": models.Language,
            "clipboard": list(),
            "data": load_to_json(row[17]),
        },
    }


def handle_movie_metadata(
    row: np.ndarray, related_models: Dict
) -> Dict[str, Union[str, int, List]]:
    """ Matches appropriate columns from the row to MovieMetadata arguments. """

    return {
        "id": row[5],
        "adult": row[0],
        "budget": row[2],
        "genres": related_models["genres"]["clipboard"],
        "homepage": row[4],
        "original_language": row[7],
        "original_title": row[8],
        "overview": row[9],
        "popularity": row[10],
        "poster_path": row[11],
        "production_companies": related_models["companies"]["clipboard"],
        "production_countries": related_models["countries"]["clipboard"],
        "release_date": row[14],
        "runtime": row[16],
        "spoken_languages": related_models["languages"]["clipboard"],
        "tagline": row[19],
        "title": row[20],
        "vote_average": row[22],
        "vote_count": row[23],
    }


def upload_movies_metadata(session: Session, row: np.ndarray) -> Iterator:
    """ Creates and yields instances of MovieMetadata and related models from data from the row. """

    row = validate_adult(row)
    row = validate_runtime(row)
    related_models = handle_related_models(row)
    for model in related_models.values():
        for item in model["data"]:
            record = model["model"].get_or_create(session, **item)
            if record:
                model["clipboard"].append(record)
    movie_metadata = handle_movie_metadata(row, related_models)
    record = models.MovieMetadata.get_or_create(session, **movie_metadata)
    if record:
        yield record


def prepare_actor_or_crew_member_data(data: Dict, movie_id: int) -> Dict:
    """ Prepares data for creating an instance od Actor or CrewMember model. """

    return {
        "id": data["id"],
        "name": data["name"],
        "gender": data["gender"],
        "profile_path": data["profile_path"],
        "movie_id": movie_id,
    }


def add_actors_or_crew(
    session: Session,
    data: str,
    movie_id: int,
    model: Union[models.Actor, models.CrewMember],
) -> Iterator:
    """ Creates an instances of Actor or CrewMember model. """

    loaded_data = load_to_json(data)
    for item in loaded_data:
        data = prepare_actor_or_crew_member_data(item, movie_id)
        record = model.create_or_update(session, **data)
        yield record


def upload_movies_credits(session: Session, row: np.ndarray) -> Iterator:
    """ Creates and yields instances of Credits and related models from data from the row. """

    movie_id = row[2]
    actors = list()
    for actor in add_actors_or_crew(session, row[0], movie_id, models.Actor):
        actors.append(actor)
        yield actor
    crew_members = list()
    for member in add_actors_or_crew(session, row[1], movie_id, models.CrewMember):
        crew_members.append(member)
        yield member
    yield models.Credits.get_or_create(
        session, id=movie_id, actors=actors, crew_members=crew_members
    )


def upload_movies_keywords(session: Session, row: np.ndarray) -> Iterator:
    """ Creates and yields instances of Keywords from data from the row. """

    yield models.Keywords.get_or_create(session, id=row[0], keywords=row[1])


def upload_movies(session: Session) -> Iterator:
    movies_metadata = session.query(models.MovieMetadata).order_by(models.MovieMetadata.id)
    movies_credits = session.query(models.Credits).order_by(models.Credits.id)
    movies_keywords = session.query(models.Keywords).order_by(models.Keywords.id)
    queried_data = (movies_metadata, movies_credits, movies_keywords)

    for (_metadata, _credits, _keywords) in zip_longest(*queried_data):
        yield models.Movie.get_or_create(
            session,
            id=_metadata.id,
            movies_metadata=_metadata,
            credits=_credits,
            keywords=_keywords,
        )


def upload_data_to_db(
    session: Session, data: Tuple[np.ndarray, np.ndarray, np.ndarray]
) -> Iterator:
    """ Uploads data to the database. """

    for row in data[0]:
        yield from upload_movies_metadata(session, row)
    for row in data[1]:
        yield from upload_movies_credits(session, row)
    for row in data[2]:
        yield from upload_movies_keywords(session, row)
    yield from upload_movies(session)


if __name__ == "__main__":
    db_man = DBManager()
    db_man.create_tables()
    engine = db_man.default_db_engine
    data = upload_csv()
    open_session(engine, upload_data_to_db, data)
