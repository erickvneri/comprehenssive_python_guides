import os
from configparser import ConfigParser

__ENV__ = os.getenv("ENV") or "development"

config = ConfigParser()
config.read("config.ini")


class env:
    PG_HOST = config.get(__ENV__, "pg_host")
    PG_PORT = config.getint(__ENV__, "pg_port")
    PG_USER = config.get(__ENV__, "pg_user")
    PG_PASSWORD = config.get(__ENV__, "pg_password")
    PG_DBNAME = config.get(__ENV__, "pg_dbname")
