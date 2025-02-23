"""
Модуль для работы с таблицей медиа.
"""

from typing import Sequence

from sqlalchemy import Row, RowMapping, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import MediaModel, TweetMediaAssociation

from .repository import ManagerRepository


class MediaRepository(ManagerRepository):
    """
    Класс - репозиторий с методами по работе с таблицей медиа.
    """

    model = MediaModel

    @classmethod
    async def delete_media_and_return_attachments(
        cls, session: AsyncSession, tweet_id: int
    ) -> Sequence[Row[str] | RowMapping | str]:
        """
        Удаляет записи из таблицы медиа по id твита.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        tweet_id: Идентификатор твита

        Возвращает пути к файлам у удаленных записей.
        """
        subquery = select(TweetMediaAssociation.media_id).filter(
            TweetMediaAssociation.tweet_id == tweet_id
        )  # Подзапрос вытаскивает идентификаторы записей таблицы медиа, которые связаны с твитом
        query = (
            delete(cls.model)
            .filter(cls.model.id.in_(subquery))
            .returning(cls.model.attachment)
        )  # Запрос удаляет записи в таблице медиа и возвращает пути к файлам.
        result = await session.execute(query)
        return result.scalars().all()
