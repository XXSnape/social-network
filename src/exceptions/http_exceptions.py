"""
Модуль с исключениями HTTPException.
"""

from fastapi import HTTPException, status

from .errors import TWEET_NOT_FOUND_ERROR, UNAUTHORIZED_ERROR, USER_NOT_FOUND_ERROR

AUTHORIZATION_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=UNAUTHORIZED_ERROR,
)

USER_NOT_EXISTS_EXCEPTION = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_ERROR
)


TWEET_NOT_FOUND_EXCEPTION = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail=TWEET_NOT_FOUND_ERROR
)
