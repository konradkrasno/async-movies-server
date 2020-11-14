""" Provides settings for the application. """

import json
import os
import re

with open("secure.json", "r") as file:
    secure = json.load(file)


def get_server_host(main_dir: os.path) -> str:
    host_dir = os.path.join(main_dir, "etc/hosts")
    try:
        with open(host_dir) as f:
            return re.match(r"([0-9]*(\.))*[0-9]*", list(f).pop()).group()
    except FileNotFoundError:
        return "127.0.0.1"


MAIN_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
HOST = get_server_host(MAIN_DIR)

# Server
SERVER = {
    "HOST": HOST,
    "PORT": 12345,
}

# Database
DATABASE = {
    "NAME": "postgres",
    "USER": "postgres",
    "PASSWORD": secure["PG_PASSWORD"],
    "HOST": "172.17.0.4",
}