"""
Модуль с контроллерами пользователей.
"""

from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db_helper import db_helper
from src.dependencies.users import get_user
from src.schemas.generic import ResultSchema
from src.schemas.users import UserCreatedSchema, UserInSchema, UserProfileSchema
from src.services.user_service import UserFollowerService, UserService
from src.types.path import FromOneToMlnPath

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserCreatedSchema)
async def create_user(
    user: UserInSchema,
    session: AsyncSession = Depends(db_helper.get_async_session),
) -> dict[str, bool | int | Any]:
    """
    Создает пользователя в базе данных.

    Параметры:

    user: Данные пользователя, которые нужно сохранить в базу
    session: Сессия для асинхронной работы с базой данных

    Возвращает словарь с именем и id сохраненного пользователя, и статусом операции.
    """
    return await UserService.create_user(session=session, user_data=user.model_dump())


@router.get("/me", response_model=UserProfileSchema)
async def get_my_info(
    session: AsyncSession = Depends(db_helper.get_async_session),
    user=Depends(get_user),
) -> dict[str, bool | dict[str, list[dict[str, Any]] | Any]]:
    """
    Отдает информацию о пользователе, который отправил запрос.

    Параметры:

    session: Сессия для асинхронной работы с базой данных
    user: Пользователь, отправивший запрос

    Возвращает словарь с данными о пользователе и статусом операции.
    """
    return await UserService.get_user_profile(session=session, user_id=user.id)


@router.delete("/{user_id}/follow", response_model=ResultSchema)
async def subscribe_to_user_by_id(
    user_id: FromOneToMlnPath,
    session: AsyncSession = Depends(db_helper.get_async_session),
    user=Depends(get_user),
) -> dict[str, bool]:
    """
    Подписывает пользователя, отправившего запрос, на другого пользователя по его id.

    Параметры:

    user_id: Идентификатор пользователя, на которого нужно подписаться
    session: Сессия для асинхронной работы с базой данных
    user: Пользователь, отправивший запрос

    Возвращает словарь со статусом операции.
    """
    return await UserFollowerService.subscribe_to_user(
        session=session, user_id=user_id, follower_id=user.id
    )


@router.get("/{user_id}", response_model=UserProfileSchema)
async def get_user_info(
    user_id: FromOneToMlnPath,
    session: AsyncSession = Depends(db_helper.get_async_session),
) -> dict[str, bool | dict[str, list[dict[str, Any]] | Any]]:
    """
    Получает информацию о пользователе по его id.

    Параметры:

    user_id: Идентификатор пользователя, о котором запрашивается информация
    user: Пользователь, отправивший запрос

    Возвращает словарь с данными о пользователе и статусом операции.
    """
    return await UserService.get_user_profile(session=session, user_id=user_id)
