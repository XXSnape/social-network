"""
Модуль с сервисами, управляющими взаимодействием пользователей и твитов.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.errors import (
    LIKE_EXISTS_ERROR,
    LIKE_NOT_EXISTS_ERROR,
    TWEET_NOT_FOUND_ERROR,
)
from src.repositories.user_tweet_repository import LikeRepository


class LikeService:
    """
    Сервис по управлению лайками.
    """

    @classmethod
    async def like_tweet(
        cls, session: AsyncSession, tweet_id: int, user_id: int
    ) -> dict[str, bool]:
        """
        Ставит лайк твиту.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        tweet_id: Идентификатор твита, которому нужно поставить лайк

        user_id: Идентификатор пользователя, который хочет поставить лайк

        Возвращает словарь со статусом операции.
        """
        result = await LikeRepository.create_object(
            session=session,
            data={"tweet_id": tweet_id, "user_id": user_id},
            exception_detail=LIKE_EXISTS_ERROR,
            exception_foreign_constraint_detail=TWEET_NOT_FOUND_ERROR,
        )
        return {"result": bool(result)}

    @classmethod
    async def delete_like(
        cls, session: AsyncSession, tweet_id: int, user_id: int
    ) -> dict[str, bool]:
        """
        Убирает лайк с твита.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        tweet_id: Идентификатор твита, с которого нужно снять лайк

        user_id: Идентификатор пользователя, который хочет снять лайк

        Возвращает словарь со статусом операции.
        """
        result = await LikeRepository.delete_object_by_params(
            session=session,
            data={"tweet_id": tweet_id, "user_id": user_id},
            exception_detail=LIKE_NOT_EXISTS_ERROR,
        )
        return {"result": bool(result)}
