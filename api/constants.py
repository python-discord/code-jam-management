from asyncpg import create_pool
from decouple import config

DATABASE_URL = config("DATABASE_URL")
MAX_POOL_SIZE = config("MAX_POOL_SIZE", cast=int, default=5)
MIN_POOL_SIZE = config("MIN_POOL_SIZE", cast=int, default=2)
DATABASE_POOL = create_pool(
    DATABASE_URL, max_size=MAX_POOL_SIZE, min_size=MIN_POOL_SIZE
)  # Will be awaited on startup

LOG_LEVEL = config("LOG_LEVEL", "INFO")
