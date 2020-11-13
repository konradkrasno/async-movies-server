from typing import *

import json
import sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User

with open("secure.json", "r") as file:
    secure = json.load(file)
DSN = f'postgresql+psycopg2://postgres:{secure["PG_PASSWORD"]}@172.17.0.2/postgres'


def connect(dsn: str) -> sqlalchemy.engine:
    return create_engine(DSN, echo=False)


def create_tables(engine: sqlalchemy.engine) -> None:
    Base.metadata.create_all(engine)


def start_session(engine: sqlalchemy.engine):
    return sessionmaker(bind=engine)()


def add_data(session) -> None:
    ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')
    session.add(ed_user)
    our_user = session.query(User).filter_by(name='ed').first()
    print(our_user)
    session.add_all([
        User(name='wendy', fullname='Wendy Williams', nickname='windy'),
        User(name='mary', fullname='Mary Contrary', nickname='mary'),
        User(name='fred', fullname='Fred Flintstone', nickname='freddy')])
    session.commit()


def get_all_data(session) -> None:
    for instance in session.query(User).order_by(User.id):
        print(instance.name, instance.fullname)


if __name__ == '__main__':
    engine = connect(DSN)
    # add check if tables not exists
    # create_tables(engine)
    session = start_session(engine)
    # add check if data is not exists in db
    # add_data(session)
    get_all_data(session)
