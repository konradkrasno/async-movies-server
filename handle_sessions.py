""" Provides tools for handling the database sessions. """

from typing import *

from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InvalidRequestError, ProgrammingError
from functools import wraps


class HandleSession:
    """ Context manager for handling database sessions. """

    def __init__(self, engine: Engine):
        self.engine = engine
        self.session = sessionmaker(bind=self.engine)()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        self.session.bind.dispose()


def open_session(engine: Engine, func: Callable, data: Any):
    """ Wrapper for open the database session and add records to the database. """

    with HandleSession(engine) as handle:
        for record in func(handle.session, data):
            try:
                handle.session.add(record)
            except InvalidRequestError:
                pass
            else:
                try:
                    handle.session.commit()
                except (IntegrityError, ProgrammingError, InvalidRequestError):
                    pass
