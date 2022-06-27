from typing import NamedTuple

from decouple import config


class Config(NamedTuple):
    """Basic configuration for the Code Jam Management System."""

    DATABASE_URL = config("DATABASE_URL")
    LOG_LEVEL = config("LOG_LEVEL", "INFO")
    DEBUG = config("DEBUG", cast=bool, default=False)
    TOKEN = config("API_TOKEN", cast=str, default="badbot13m0n8f570f942013fc818f234916ca531")
