"""
Модуль с исключениями RequestValidationError.
"""

from fastapi.exceptions import RequestValidationError

from .errors import (
    FILE_EXTENSION_ERROR,
    LARGE_NUMBER_ERROR,
    SUBSCRIPTION_ERROR,
    USER_NOT_CREATED_ERROR,
)

INCORRECT_FILE_EXTENSION_EXCEPTION = RequestValidationError(errors=FILE_EXTENSION_ERROR)

INCOMPATIBLE_DATA_EXCEPTION = RequestValidationError(errors=SUBSCRIPTION_ERROR)

LARGE_NUMBER_EXCEPTION = RequestValidationError(errors=LARGE_NUMBER_ERROR)
USER_NOT_CREATED_EXCEPTION = RequestValidationError(errors=USER_NOT_CREATED_ERROR)
