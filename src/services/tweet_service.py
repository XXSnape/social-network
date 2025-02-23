"""
Модуль с сервисами, управляющими твитами.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.errors import PICTURE_NOT_FOUND_ERROR, TWEET_NOT_CREATED_ERROR
from src.exceptions.http_exceptions import TWEET_NOT_FOUND_EXCEPTION
from src.exceptions.request_exceptions import LARGE_NUMBER_EXCEPTION
from src.repositories.tweet_media_repository import TweetMediaRepository
from src.repositories.tweets import TweetRepository
from src.schemas.tweets import TweetContentSchema, TweetsOutputSchema

from .media_service import MediaService


class TweetService:
    """
    Сервис по работе с твитами
    """

    @classmethod
    async def get_tweets_user(
        cls, session: AsyncSession, offset: int | None, limit: int | None
    ) -> TweetsOutputSchema:
        """
        Получает все твиты.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        offset: с какого твита нужно показывать оставшиеся
        limit: ограничение количество твитов

        Возвращает словарь со всеми твитами и статусом операции.
        """
        tweets = await TweetRepository.get_user_tweets(
            session=session, offset=offset, limit=limit
        )
        tweet_models = [
            TweetContentSchema.model_validate(tweet, from_attributes=True)
            for tweet in tweets
        ]
        return TweetsOutputSchema(result=True, tweets=tweet_models)

    @classmethod
    async def add_media_to_tweet(
        cls,
        session: AsyncSession,
        tweet_id: int,
        media_ids: list[int],
    ) -> None:
        """
        Связывает картинки с твитом по id картинок без коммита.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        tweet_id: Идентификатор твита, к которому прикрепляются картинки
        media_ids: Список с идентификаторами картинок
        """
        for media_id in media_ids:
            await TweetMediaRepository.create_object(
                session=session,
                data={"tweet_id": tweet_id, "media_id": media_id},
                exception_foreign_constraint_detail=PICTURE_NOT_FOUND_ERROR,
                commit_need=False,
            )

    @classmethod
    async def create_tweet(
        cls, session: AsyncSession, tweet_data: dict
    ) -> dict[str, bool | int]:
        """
        Создает твит и прикрепляет к нему картинки.
        Коммит происходит только при успешном добавлении всех картинок к твиту.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        tweet_data: Словарь с данными о твите

        Возвращает словарь с идентификатором твита и статусом операции.
        """
        media_ids = tweet_data.pop("tweet_media_ids")
        if not all(media_id < 10**6 for media_id in media_ids):
            raise LARGE_NUMBER_EXCEPTION
        tweet_data["content"] = tweet_data.pop("tweet_data")
        tweet_id = await TweetRepository.create_object(
            session=session,
            data=tweet_data,
            commit_need=False,
            exception_detail=TWEET_NOT_CREATED_ERROR,
        )

        await cls.add_media_to_tweet(session, tweet_id=tweet_id, media_ids=media_ids)
        await session.commit()
        return {"result": True, "tweet_id": tweet_id}

    @classmethod
    async def delete_tweet(
        cls, session: AsyncSession, tweet_id: int, user_id: int
    ) -> dict[str, bool]:
        """
        Удаляет твит, картинки твита из базы и сервера.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        tweet_id: Идентификатор твита
        user_id: Идентификатор пользователя, создавшего твит

        Возвращает словарь со статусом операции.
        """
        data = {"id": tweet_id, "user_id": user_id}
        if not await TweetRepository.check_exists_object_by_params(
            session=session, data=data
        ):
            raise TWEET_NOT_FOUND_EXCEPTION
        await MediaService.delete_media_from_disk_by_tweet_id(
            session=session, tweet_id=tweet_id
        )
        result = await TweetRepository.delete_object_by_params(
            session=session, data=data
        )
        return {"result": result}
