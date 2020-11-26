""" Provides settings for the application. """

import json
import re

from pathlib import Path


def get_server_host(main_dir: Path) -> str:
    host_dir = main_dir / "etc/hosts"
    try:
        with open(host_dir) as f:
            return re.match(r"([0-9]*(\.))*[0-9]*", list(f).pop()).group()
    except FileNotFoundError:
        return "127.0.0.1"


BASE_DIR = Path(__file__).resolve().parent
MAIN_DIR = BASE_DIR.parent.parent.parent
HOST = get_server_host(MAIN_DIR)

with open(BASE_DIR / "secure.json", "r") as file:
    secure = json.load(file)


# Server
SERVER = {
    "HOST": HOST,
    "PORT": 12345,
}

# Database
DATABASES = {
    "default": {
        "NAME": "movies-db",
        "USER": "postgres",
        "PASSWORD": secure["PG_PASSWORD"],
        "HOST": "localhost",
        "PORT": 5432,
    },
    "docker": {
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": secure["PG_PASSWORD"],
        "HOST": "172.17.0.2",
        "PORT": 5432,
    },
    "test": {
        "NAME": "test",
        "USER": "postgres",
        "PASSWORD": secure["PG_PASSWORD"],
        "HOST": "localhost",
        "PORT": 5432,
    },
}
