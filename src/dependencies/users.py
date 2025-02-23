"""
Модуль для работы с зависимостями пользователей.
"""

from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db_helper import db_helper
from src.exceptions.http_exceptions import AUTHORIZATION_EXCEPTION
from src.schemas.users import UserSchema
from src.services.user_service import UserService


async def get_user(
    token: Annotated[str, Header(alias="api-key")],
    session: AsyncSession = Depends(db_helper.get_async_session),
) -> UserSchema:
    """
    Получает пользователя из базы данных по токену.

    Параметры:

    token: Строка, являющаяся идентификатором пользователя
    session: Сессия для асинхронной работы с базой данных

    Если пользователя с таким токеном в базе не оказалось, вызывается исключение со статусом 401.
    Возвращается UserSchema с данными пользователя.
    """
    user = await UserService.get_user_by_token(session=session, token=token)
    if not user:
        raise AUTHORIZATION_EXCEPTION
    return user
