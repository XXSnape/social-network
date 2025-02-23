"""
Модуль с контроллерами твитов.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db_helper import db_helper
from src.dependencies.users import get_user
from src.schemas.generic import ResultSchema
from src.schemas.tweets import TweetInResultSchema, TweetInSchema, TweetsOutputSchema
from src.services.tweet_service import TweetService
from src.services.user_service import UserFollowerService
from src.services.user_tweet_service import LikeService
from src.types.path import FromOneToMlnPath
from src.types.query import FromOneToMlnQuery

router = APIRouter(prefix="/tweets", tags=["/tweets"])


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=TweetInResultSchema
)
async def create_tweet_user(
    tweet: TweetInSchema,
    session: AsyncSession = Depends(db_helper.get_async_session),
    user=Depends(get_user),
) -> dict[str, bool | int]:
    """
    Сохраняет твит в базу данных.

    Параметры:

    tweet: Данные твита, которые нужно сохранить
    session: Сессия для асинхронной работы с базой данных
    user: Пользователь, отправивший запрос

    Возвращает словарь с id сохраненного твита и статусом операции.
    """
    tweet_data = tweet.model_dump()
    tweet_data["user_id"] = user.id
    return await TweetService.create_tweet(session=session, tweet_data=tweet_data)


@router.get("", response_model=TweetsOutputSchema, dependencies=[Depends(get_user)])
async def get_tweets_user(
    offset: FromOneToMlnQuery = None,
    limit: FromOneToMlnQuery = None,
    session: AsyncSession = Depends(db_helper.get_async_session),
) -> TweetsOutputSchema:
    """
    Получает все существующие твиты.

    Параметры:

    session: Сессия для асинхронной работы с базой данных
    offset: с какого твита нужно показывать оставшиеся
    limit: ограничение количество твитов

    Возвращает словарь со всеми твитами и статусом операции.
    """
    return await TweetService.get_tweets_user(
        session=session, offset=offset, limit=limit
    )


@router.delete("/{tweet_id}", response_model=ResultSchema)
async def delete_tweet_user(
    tweet_id: FromOneToMlnPath,
    session: AsyncSession = Depends(db_helper.get_async_session),
    user=Depends(get_user),
) -> dict[str, bool]:
    """
    Удаляет твит по id.

    Параметры:

    tweet_id: Идентификатор твита
    session: Сессия для асинхронной работы с базой данных
    user: Пользователь, отправивший запрос

    Возвращает словарь со статусом операции.
    """
    return await TweetService.delete_tweet(
        session=session, tweet_id=tweet_id, user_id=user.id
    )


@router.post("/{tweet_id}/likes", response_model=ResultSchema)
async def like_tweet(
    tweet_id: FromOneToMlnPath,
    session: AsyncSession = Depends(db_helper.get_async_session),
    user=Depends(get_user),
) -> dict[str, bool]:
    """
    Лайкает твит по id.

    Параметры:

    tweet_id: Идентификатор твита
    session: Сессия для асинхронной работы с базой данных
    user: Пользователь, отправивший запрос

    Возвращает словарь со статусом операции.
    """
    return await LikeService.like_tweet(
        session=session, tweet_id=tweet_id, user_id=user.id
    )


@router.delete("/{tweet_id}/likes", response_model=ResultSchema)
async def delete_like_tweet(
    tweet_id: FromOneToMlnPath,
    session: AsyncSession = Depends(db_helper.get_async_session),
    user=Depends(get_user),
) -> dict[str, bool]:
    """
    Удаляет лайк по id твита.

    Параметры:

    tweet_id: Идентификатор твита
    session: Сессия для асинхронной работы с базой данных
    user: Пользователь, отправивший запрос

    Возвращает словарь со статусом операции.
    """
    return await LikeService.delete_like(
        session=session, tweet_id=tweet_id, user_id=user.id
    )


@router.delete("/{user_id}/follow", response_model=ResultSchema)
async def unsubscribe_to_user_by_id(
    user_id: FromOneToMlnPath,
    session: AsyncSession = Depends(db_helper.get_async_session),
    user=Depends(get_user),
) -> dict[str, bool]:
    """
    Отписывает пользователя, отправившего запрос, от другого пользователя по его id.

    Параметры:

    user_id: Идентификатор пользователя, от которого нужно отписаться
    session: Сессия для асинхронной работы с базой данных
    user: Пользователь, отправивший запрос

    Возвращает словарь со статусом операции.
    """
    return await UserFollowerService.unsubscribe_from_user(
        session=session, user_id=user_id, follower_id=user.id
    )
