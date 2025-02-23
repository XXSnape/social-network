"""
Модуль для работы с таблицей твитов.
"""

from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import LikeModel, TweetModel

from .repository import ManagerRepository


class TweetRepository(ManagerRepository):
    """
    Класс - репозиторий для работы с таблицей твитов.
    """

    model = TweetModel

    @classmethod
    async def get_user_tweets(
        cls, session: AsyncSession, offset: int | None, limit: int | None
    ) -> Sequence[TweetModel]:
        """
        Получает все существующие твиты. Присоединяет к ним авторов, картинки, лайки.
        Сортирует по количеству лайков и id.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        offset: с какого твита нужно показывать оставшиеся
        limit: ограничение количество твитов

        Возвращает твиты.
        """
        query = (
            select(cls.model)
            .outerjoin(LikeModel, LikeModel.tweet_id == cls.model.id)
            .options(selectinload(cls.model.author))
            .options(selectinload(cls.model.attachments))
            .options(selectinload(cls.model.likes))
            .group_by(cls.model.id)
            .order_by(func.count(LikeModel.id).desc(), cls.model.id.desc())
        )
        if offset and limit:
            query = query.offset((offset - 1) * limit).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()
