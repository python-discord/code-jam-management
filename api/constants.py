from decouple import config

DATABASE_URL = config("DATABASE_URL")
LOG_LEVEL = config("LOG_LEVEL", "INFO")
DEBUG = config("DEBUG", cast=bool, default=False)
TOKEN = config("API_TOKEN", cast=str, default="badbot13m0n8f570f942013fc818f234916ca531")
