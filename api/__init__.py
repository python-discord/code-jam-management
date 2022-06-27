import logging

from api import constants

format_string = "[%(asctime)s] [%(process)d] [%(levelname)s] %(name)s - %(message)s"
date_format_string = "%Y-%m-%d %H:%M:%S %z"

logging.basicConfig(
    format=format_string,
    datefmt=date_format_string,
    level=getattr(logging, constants.Config.LOG_LEVEL.upper())
)

logging.getLogger().info("Logging initialization complete")
