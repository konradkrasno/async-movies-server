""" Provides tools for handling the database sessions. """

from typing import *

from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

import logging
import datetime


class HandleSession:
    """ Context manager for handling database sessions. """

    def __init__(self, engine: Engine):
        logging.info(f" {datetime.datetime.now()}: Starting session.")
        self.engine = engine
        self.session = sessionmaker(bind=self.engine)()

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info(f" {datetime.datetime.now()}: Closing session.")
        self.session.close()
        self.session.bind.dispose()


def open_session(engine: Engine, func: Callable, data: Any):
    """ Wrapper for open the database session and add records to the database. """

    with HandleSession(engine) as handle:
        start = datetime.datetime.now()
        logging.info(f" {start}: Uploading data...")
        for record in func(handle.session, data):
            handle.session.add(record)
            try:
                handle.session.commit()
            except Exception as e:
                logging.error(f"An error occurred when committing record: {record}. Error info: {e}")
                handle.session.rollback()
        finish = datetime.datetime.now()
        delta = (finish - start)/60
        logging.info(f" It lasts {delta} minutes.")
