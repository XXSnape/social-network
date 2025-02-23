"""
Модуль с сервисами, управляющими пользователями.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.errors import (
    SUBSCRIPTION_EXISTS_ERROR,
    SUBSCRIPTION_NOT_EXISTS_ERROR,
    USER_NOT_CREATED_ERROR,
    USER_NOT_FOUND_ERROR,
)
from src.exceptions.http_exceptions import USER_NOT_EXISTS_EXCEPTION
from src.exceptions.request_exceptions import INCOMPATIBLE_DATA_EXCEPTION
from src.repositories.users import UserFollowerRepository, UserRepository
from src.schemas.users import UserOutputSchema, UserSchema

from .utils import get_hash_token


class UserService:
    """
    Сервис по управлению пользователями.
    """

    @classmethod
    async def create_user(
        cls, session: AsyncSession, user_data: dict
    ) -> dict[str, bool | int | Any]:
        """
        Создает пользователя.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        user_data: Словарь с данными о пользователе

        Возвращает словарь с именем и id сохраненного пользователя, и статусом операции.
        """
        result = await UserRepository.create_object(
            session=session,
            data={
                "name": user_data["name"],
                "token": get_hash_token(user_data["token"]),
            },
            exception_detail=USER_NOT_CREATED_ERROR,
        )
        return {"result": True, "id": result, "name": user_data["name"]}

    @classmethod
    async def get_user_by_token(
        cls, session: AsyncSession, token: str
    ) -> UserSchema | None:
        """
        Получает пользователя по токену.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        token: Личный токен пользователя

        Возвращает схему пользователя или None.
        """
        result = await UserRepository.get_object_by_params(
            session=session, data={"token": get_hash_token(token)}
        )
        if result:
            return UserSchema.model_validate(result)
        return result

    @classmethod
    async def get_user_profile(
        cls, session: AsyncSession, user_id: int
    ) -> dict[str, bool | dict[str, list[dict[str, Any]] | Any]]:
        """
        Получает информацию о профиле пользователя.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        user_id: Идентификатор пользователя

        Возвращает словарь с данными о пользователе и статусом операции.
        """
        user = await UserRepository.get_user_followers_and_following(
            session=session, user_id=user_id
        )
        if not user:
            raise USER_NOT_EXISTS_EXCEPTION
        model_json = UserOutputSchema.model_validate(
            user, from_attributes=True
        ).model_dump()
        return {"result": True, "user": model_json}


class UserFollowerService:
    """
    Сервис по управлению подписчиками пользователей.
    """

    @classmethod
    def check_user_match(cls, user_id: int, follower_id: int) -> None:
        """
        Валидирует данные.
        Если пользователь хочет подписаться или отписаться от самого себя, вызывается исключение.

        Параметры:

        user_id: Идентификатор пользователя
        follower_id: Идентификатор подписчика
        """
        if user_id == follower_id:
            raise INCOMPATIBLE_DATA_EXCEPTION

    @classmethod
    async def subscribe_to_user(
        cls, session: AsyncSession, user_id: int, follower_id: int
    ) -> dict[str, bool]:
        """
        Подписывает пользователя с идентификатором user_id на пользователя с идентификатором follower_id.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        user_id: Идентификатор пользователя
        follower_id: Идентификатор пользователя, на которого нужно подписаться

        Возвращает словарь со статусом операции.
        """
        cls.check_user_match(user_id, follower_id)
        result = await UserFollowerRepository.create_object(
            session=session,
            data={"user_id": user_id, "follower_id": follower_id},
            exception_detail=SUBSCRIPTION_EXISTS_ERROR,
            exception_foreign_constraint_detail=USER_NOT_FOUND_ERROR,
        )
        return {"result": bool(result)}

    @classmethod
    async def unsubscribe_from_user(
        cls, session: AsyncSession, user_id: int, follower_id: int
    ) -> dict[str, bool]:
        """
        Отписывает пользователя с идентификатором user_id от пользователя с идентификатором follower_id.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        user_id: Идентификатор пользователя
        follower_id: Идентификатор пользователя, от которого нужно отписаться

        Возвращает словарь со статусом операции.
        """
        cls.check_user_match(user_id, follower_id)
        result = await UserFollowerRepository.delete_object_by_params(
            session=session,
            data={"user_id": user_id, "follower_id": follower_id},
            exception_detail=SUBSCRIPTION_NOT_EXISTS_ERROR,
        )
        return {"result": bool(result)}
