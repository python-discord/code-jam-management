from decouple import config

DATABASE_URL = config("DATABASE_URL")
LOG_LEVEL = config("LOG_LEVEL", "INFO")
