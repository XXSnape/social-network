"""
Модуль для работы с таблицей пользователей.
"""

from typing import Sequence

from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only, selectinload

from src.models import FollowerModel, UserModel

from .repository import ManagerRepository


class UserRepository(ManagerRepository):
    """
    Класс - репозиторий для работы с таблицей пользователей.
    """

    model = UserModel

    @classmethod
    async def get_user_followers_and_following(
        cls, session: AsyncSession, user_id: int
    ) -> UserModel | None:
        query = (
            select(UserModel)
            .options(
                load_only(UserModel.id, UserModel.name),
                selectinload(UserModel.followers).load_only(
                    UserModel.id, UserModel.name
                ),
                selectinload(UserModel.following).load_only(
                    UserModel.id, UserModel.name
                ),
            )
            .filter(UserModel.id == user_id)
        )
        result = await session.execute(query)
        return result.scalars().one_or_none()


class UserFollowerRepository(ManagerRepository):
    """
    Класс - репозиторий для работы с таблицей подписчиков.
    """

    model = FollowerModel

    @classmethod
    async def get_followers_user(
        cls, session: AsyncSession, user_id: int
    ) -> Sequence[Row[tuple[int, str]]]:
        """
        Получает подписчиков пользователя по id.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        user_id: Идентификатор пользователя

        Возвращает id и имена подписчиков пользователя.
        """
        query = (
            select(UserModel.id, UserModel.name)
            .join(cls.model, cls.model.follower_id == UserModel.id)
            .filter(cls.model.user_id == user_id)
        )
        result = await session.execute(query)
        return result.all()

    @classmethod
    async def get_following_user(
        cls, session: AsyncSession, user_id: int
    ) -> Sequence[Row[tuple[int, str]]]:
        """
        Получает юзеров, у которых в подписчиках есть пользователь с идентификатором user_id.

        Параметры:

        session: Сессия для работы с асинхронной базой данных
        user_id: Идентификатор пользователя

        Возвращает id и имена юзеров, на которых подписан пользователь с идентификатором user_id.
        """
        query = (
            select(UserModel.id, UserModel.name)
            .join(cls.model, cls.model.user_id == UserModel.id)
            .filter(cls.model.follower_id == user_id)
        )
        result = await session.execute(query)
        return result.all()
