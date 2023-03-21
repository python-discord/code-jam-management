"""Utilities for working with the project's constants."""
import logging
import typing
from collections.abc import Sequence

import pydantic
from pydantic.error_wrappers import ErrorWrapper

logger = logging.getLogger("cjms.settings")

# This is available in pydantic as pydantic.error_wrappers.ErrorList
# but is typehinted as a Sequence[any], due to being a recursive type.
# This makes it harder to handle the types.
# For our purposes, a fully accurate representation is not necessary.
_PYDANTIC_ERROR_TYPE = Sequence[ErrorWrapper | Sequence[ErrorWrapper]]


class CJMSBaseSettings(pydantic.BaseSettings):
    """Base class for settings with .env support and nicer error messages."""

    @staticmethod
    def __log_missing_errors(base_error: pydantic.ValidationError, errors: _PYDANTIC_ERROR_TYPE) -> bool:
        """
        Log out a nice representation for missing environment variables.

        Returns false if none of the errors were caused by missing variables.
        """
        found_relevant_errors = False
        for error in errors:
            if isinstance(error, Sequence):
                found_relevant_errors = (
                    CJMSBaseSettings.__log_missing_errors(base_error, error) or found_relevant_errors
                )
            elif isinstance(error.exc, pydantic.MissingError):
                logger.error(f"Missing environment variable {base_error.args[1].__name__}.{error.loc_tuple()[0]}")
                found_relevant_errors = True

        return found_relevant_errors

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Try to instantiate the class, and print a nicer message for unset variables."""
        try:
            super().__init__(*args, **kwargs)
        except pydantic.ValidationError as error:
            if CJMSBaseSettings.__log_missing_errors(error, error.raw_errors):
                exit(1)
            else:
                # The validation error is not due to an unset environment variable, propagate the error as normal
                raise error from None

    class Config:
        """Enable env files."""

        frozen = True

        env_file = ".env"
        env_file_encoding = "utf-8"
