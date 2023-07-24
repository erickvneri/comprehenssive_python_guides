import os
from configparser import ConfigParser


__ENV__ = os.getenv("ENV", "development")


config = ConfigParser()
config.read("config.ini")


class env:
    DB_URL = config.get(__ENV__, "db_url")
