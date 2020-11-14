from typing import *

import sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import DATABASE
from models import Base, User


def connect() -> sqlalchemy.engine:
    dsn = "postgresql+psycopg2://%s:%s@%s/%s" % (
        DATABASE["USER"],
        DATABASE["PASSWORD"],
        DATABASE["HOST"],
        DATABASE["NAME"],
    )
    return create_engine(dsn, echo=False)


def create_tables(engine: sqlalchemy.engine) -> None:
    Base.metadata.create_all(engine)


def start_session(engine: sqlalchemy.engine):
    return sessionmaker(bind=engine)()


def add_data(session) -> None:
    ed_user = User(name="ed", fullname="Ed Jones", nickname="edsnickname")
    session.add(ed_user)
    our_user = session.query(User).filter_by(name="ed").first()
    print(our_user)
    session.add_all(
        [
            User(name="wendy", fullname="Wendy Williams", nickname="windy"),
            User(name="mary", fullname="Mary Contrary", nickname="mary"),
            User(name="fred", fullname="Fred Flintstone", nickname="freddy"),
        ]
    )
    session.commit()


def get_all_data(session) -> None:
    for instance in session.query(User).order_by(User.id):
        print(instance.name, instance.fullname)


if __name__ == "__main__":
    engine = connect()
    # add check if tables not exists
    # create_tables(engine)
    session = start_session(engine)
    # add check if data is not exists in db
    # add_data(session)
    get_all_data(session)
