"""
Главный файл, из которого запускается приложение.
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.routers.medias import router as media_router
from src.routers.tweets import router as tweet_router
from src.routers.users import router as user_router
from src.schemas.exceptions import ExceptionSchema
from src.services.utils import handle_errors

app = FastAPI(
    responses={
        401: {"model": ExceptionSchema},
        404: {"model": ExceptionSchema},
        422: {"model": ExceptionSchema},
    },
)
app.include_router(user_router, prefix="/api")
app.include_router(tweet_router, prefix="/api")
app.include_router(media_router, prefix="/api")


@app.exception_handler(RequestValidationError)
async def request_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Обрабатывает исключение RequestValidationError.

    Параметры:

    request: Запрос пользователя
    exc: Исключение RequestValidationError

    Возвращает JSONResponse с переопределенными значениями.
    """
    error_messages = handle_errors(errors=exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": "RequestValidationError",
                "error_messages": error_messages,
            }
        ),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Обрабатывает исключение HTTPException.

    Параметры:

    request: Запрос пользователя
    exc: Исключение HTTPException

    Возвращает JSONResponse с переопределенными значениями.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": "HTTPException",
                "error_messages": exc.detail,
            }
        ),
    )


@app.exception_handler(404)
async def not_found_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """
    Обрабатывает ошибку 404.

    Параметры:

    request: Запрос пользователя
    exc: Исключение HTTPException

    Возвращает JSONResponse с переопределенными значениями.
    """
    return await http_exception_handler(request, exc)


@app.exception_handler(405)
async def method_is_not_allowed_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """
    Обрабатывает ошибку 405.

    Параметры:

    request: Запрос пользователя
    exc: Исключение HTTPException

    Возвращает JSONResponse с переопределенными значениями.
    """
    return await http_exception_handler(request, exc)
