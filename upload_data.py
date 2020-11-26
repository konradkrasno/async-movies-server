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
from collections.abc import Iterable


def make_convertible_to_json(string: str) -> str:
    """ Processes input string to convertible to JSON. """

    keys = re.findall(r"(')(\w{1,10})(':)", string)
    for key in keys:
        string = string.replace("'{}'".format(key[1]), '"{}"'.format(key[1]))
    string = re.sub("\\'", '"', string)
    string = re.sub(r'(\w+)"(\w+)', r"\1\2", string)
    string = string.replace("None", '""')
    return string


def load_to_json(string: str) -> Iterable:
    """ Converts string to JSON and returns. If an error occurred, returns empty Dict. """

    try:
        string = make_convertible_to_json(string)
    except TypeError:
        return dict()
    try:
        result = json.loads(string)
    except json.decoder.JSONDecodeError:
        return dict()
    else:
        if isinstance(result, Iterable):
            return result
    return dict()


def upload_csv(directory: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """ Reads data from csv files. """

    movies_metadata = pd.read_csv(
        BASE_DIR / "{}/movies_metadata.csv".format(directory), low_memory=False
    )
    movies_credits = pd.read_csv(BASE_DIR / "{}/credits.csv".format(directory))
    movies_keywords = pd.read_csv(BASE_DIR / "{}/keywords.csv".format(directory))

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


def prepare_actor_or_crew_member_data(data: Dict) -> Dict:
    """ Prepares data for creating an instance of Actor or CrewMember model. """

    return {
        "id": data["id"],
        "name": data["name"],
        "gender": data["gender"],
        "profile_path": data["profile_path"],
    }


def prepare_character_data(data: Dict, actor: models.Actor, movie_id: int) -> Dict:
    """ Prepares data for creating an instance of Cast model. """

    return {
        "character": data["character"],
        "actor_id": actor.id,
        "actor": actor,
        "order": data["order"],
        "movie_id": movie_id,
    }


def prepare_crew_data(
    data: Dict, crew_member: models.CrewMember, movie_id: int
) -> Dict:
    """ Prepares data for creating an instance of Crew model. """

    return {
        "department": data["department"],
        "job": data["job"],
        "crew_member_id": crew_member.id,
        "crew_member": crew_member,
        "movie_id": movie_id,
    }


def upload_characters(session: Session, data: Iterable, movie_id: int) -> Iterator:
    """ Creates and yields instances of Actor and Cast models. """

    for item in data:
        actor_data = prepare_actor_or_crew_member_data(item)
        actor = models.Actor.get_or_create(session, **actor_data)
        yield actor
        character_data = prepare_character_data(item, actor, movie_id)
        character = models.Character.create(**character_data)
        yield character


def upload_crew(session: Session, data: Iterable, movie_id: int) -> Iterator:
    """ Creates and yields instances of CrewMember and Crew models. """

    for item in data:
        crew_member_data = prepare_actor_or_crew_member_data(item)
        crew_member = models.CrewMember.get_or_create(session, **crew_member_data)
        yield crew_member
        crew_data = prepare_crew_data(item, crew_member, movie_id)
        crew = models.Crew.create(**crew_data)
        yield crew


def upload_movies_credits(session: Session, row: np.ndarray) -> Iterator:
    """ Creates and yields instances of Credits and related models from data from the row. """

    movie_id = row[2]
    cast_data = load_to_json(row[0])
    yield from upload_characters(session, cast_data, movie_id)
    crew_data = load_to_json(row[1])
    yield from upload_crew(session, crew_data, movie_id)


def upload_movies_keywords(session: Session, row: np.ndarray) -> Iterator:
    """ Creates and yields instances of Keywords from data from the row. """

    yield models.Keywords.get_or_create(session, movie_id=row[0], keywords=row[1])


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


if __name__ == "__main__":
    from settings import DATABASES

    db_man = DBManager(db_config=DATABASES["default"])
    db_man.create_tables()
    engine = db_man.default_db_engine
    data = upload_csv("archive")
    open_session(engine, upload_data_to_db, data)
