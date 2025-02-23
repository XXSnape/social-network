"""
Модуль с тестами для приложения.
"""

import copy
import json
from datetime import datetime
from os import listdir
from typing import Any

import pytest
from fixtures.fixtures import (
    ADDED_LIKES,
    ADDED_TWEETS,
    ALL_TWEETS,
    AUTHORIZATION_ERROR,
    BAD_TOKEN,
    FOLLOWER,
    FOLLOWERS,
    FOLLOWING,
    GOOD_RESULT,
    LIKE,
    LIKES,
    METHOD_NOT_ALLOWED,
    PROFILE_DATA,
    TWEETS,
    USER,
    USERS,
)
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.medias import MediaRepository
from src.repositories.repository import AbstractRepository
from src.repositories.tweet_media_repository import TweetMediaRepository
from src.repositories.tweets import TweetRepository
from src.repositories.user_tweet_repository import LikeRepository
from src.repositories.users import UserFollowerRepository, UserRepository


def get_data_from_fixtures(filename: str) -> Any:
    """
    Десереализует файл с данными.

    Параметры:

    filename: Название файла

    Возвращает десереализованные данные.
    """
    with open(f"fixtures/{filename}", mode="r") as file:
        return json.load(file)


async def check_objects_for_existence(
    repository: AbstractRepository, session: AsyncSession, objects: list[dict]
) -> list[bool]:
    """
    Проверяет, что объекты с переданными параметрами существуют в базе.
    Используется только внутри тестов.

    Параметры:

    repository: Абстрактный репозиторий для работы с таблицами базы данных
    session: Сессия для асинхронной работы с базой данных
    objects: Список из словарей, содержащих параметры объектов

    Возвращает список из значений True или False.
    Если значение принимает True, то объект найден в базе данных. Иначе не найден.
    """
    return [
        await repository.check_exists_object_by_params(session=session, data=obj)
        for obj in objects
    ]


def good_response_test(response: Response) -> None:
    """
    Проверяет, что статус код ответа от сервера равен 200 и операция выполнена успешно.
    Используется только внутри тестов.

    Параметры:

    response: Ответ от сервера.
    """
    assert response.status_code == 200
    assert response.json() == GOOD_RESULT


def request_validation_error_test(response: Response) -> None:
    """
    Проверяет, что статус код ответа от сервера равен 422,
    и операция не была выполнена успешно из-за невалидных данных от клиента.
    Используется только внутри тестов.

    Параметры:

    response: Ответ от сервера.
    """
    response_json = response.json()
    assert response.status_code == 422
    assert response_json["result"] is False
    assert response_json["error_type"] == "RequestValidationError"
    assert isinstance(response_json["error_messages"], str)


def not_found_error_test(response: Response) -> None:
    """
    Проверяет, что статус код ответа от сервера равен 404,
    и операция не была выполнена успешно из-за того, что запрашиваемого ресурса нет на сервере.
    Используется только внутри тестов.

    Параметры:

    response: Ответ от сервера.
    """
    response_json = response.json()

    assert response.status_code == 404
    assert response_json["result"] is False
    assert response_json["error_type"] == "HTTPException"
    assert isinstance(response_json["error_messages"], str)


def authorization_error_test(response: Response) -> None:
    """
    Проверяет, что статус код ответа от сервера равен 401,
    и операция не была выполнена успешно из-за непройденной авторизации.
    Используется только внутри тестов.

    Параметры:

    response: Ответ от сервера.
    """
    assert response.status_code == 401
    assert response.json() == AUTHORIZATION_ERROR


class TestUsers:
    """
    Класс с тестами, нацеленными на взаимодействие с пользователями в базе данных, контроллере.
    """

    user1_info = copy.deepcopy(USER)  # Информация о пользователе с id 1

    @classmethod
    async def check_followers_for_existence(
        cls, async_session: AsyncSession
    ) -> list[bool]:
        """
        Получает данные из базы о подписчиках по различным параметрам.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных

        Возвращает список из трех значений. Каждое принимает True или False.
        Если значение принимает True, то подписчик найден в базе данных. Иначе не найден.
        """
        return await check_objects_for_existence(
            repository=UserFollowerRepository, session=async_session, objects=FOLLOWERS
        )

    @classmethod
    async def check_users_for_existence(cls, async_session: AsyncSession) -> list[bool]:
        """
        Получает данные из базы о пользователях по различным параметрам.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных

        Возвращает список из четырех значений. Каждое принимает True или False.
        Если значение принимает True, то пользователь найден в базе данных. Иначе не найден.
        """
        return await check_objects_for_existence(
            repository=UserRepository, session=async_session, objects=USERS
        )

    @classmethod
    async def test_no_users_in_db(cls, async_session: AsyncSession) -> None:
        """
        Проверяет, что в базе данных нет пользователей.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных
        """
        assert not any(await cls.check_users_for_existence(async_session))

    @classmethod
    @pytest.mark.parametrize("data", get_data_from_fixtures("create_users.json"))
    async def test_create_users_endpoint(
        cls, ac: AsyncClient, data: list[dict, int]
    ) -> None:
        """
        Делает запросы на создание пользователей.
        Проверяет, что статус код ответа от сервера равен 201, и тело ответа совпадает с ожиданиями.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        data: Список с данными пользователя и идентификатором, который должен вернуться в ответе
        """
        json_data, user_id = data
        response = await ac.post("api/users", json=json_data)
        assert response.status_code == 201
        assert response.json() == {
            "result": True,
            "id": user_id,
            "name": json_data["name"],
        }

    @classmethod
    async def test_check_users_in_db(cls, async_session: AsyncSession) -> None:
        """
        Проверяет, что все пользователи успешно добавлены в базу данных.

        Параметры:

        параметр async_session: Сессия для асинхронной работы с базой данных
        """
        assert all(await cls.check_users_for_existence(async_session))

    @classmethod
    async def test_get_me_info(cls, ac: AsyncClient) -> None:
        """
        Делает запрос на получение информации о пользователе, который сделал этот запрос.
        Проверяет, что статус код ответа от сервера равен 200, и тело ответа совпадает с ожиданиями.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        """
        response = await ac.get("/api/users/me", headers={"api-key": "test"})
        assert response.status_code == 200
        assert response.json() == cls.user1_info

    @classmethod
    async def test_no_followers_in_db(cls, async_session: AsyncSession) -> None:
        """
        Проверяет, что в базе данных нет подписчиков на пользователей.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных
        """
        assert not any(await cls.check_followers_for_existence(async_session))

    @classmethod
    @pytest.mark.parametrize("data", get_data_from_fixtures("follow_to_user.json"))
    async def test_follow_to_user_endpoint(
        cls, ac: AsyncClient, data: list[str, str]
    ) -> None:
        """
        Делает запросы на подписку на пользователей.
        Проверяет, что статус код ответа от сервера равен 200, и тело ответа совпадает с ожиданиями.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        data: Список с адресом ресурса и токеном пользователя, который делает запрос
        """
        url, token = data
        response = await ac.delete(url, headers={"api-key": token})
        good_response_test(response)

    @classmethod
    async def test_check_followers_in_db(cls, async_session: AsyncSession) -> None:
        """
        Проверяет, что все подписки успешно добавлены в базу данных.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных
        """
        assert all(await cls.check_followers_for_existence(async_session))

    @classmethod
    async def test_check_followers_on_page(cls, ac: AsyncClient) -> None:
        """
        После оформления подписок делает запрос на получение информации о пользователе,
        который сделал этот запрос.
        Проверяет, что статус код ответа от сервера равен 200, и тело ответа совпадает с ожиданиями.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        """
        cls.user1_info["user"]["followers"].append(FOLLOWER)
        cls.user1_info["user"]["following"].extend(FOLLOWING)
        await cls.test_get_me_info(ac)

    @classmethod
    async def test_unfollow_to_user_endpoint(cls, ac: AsyncClient) -> None:
        """
        Делает запрос на отписку пользователя с id 1 от пользователя с id 3.
        Проверяет, что статус код ответа от сервера равен 200, и тело ответа совпадает с ожиданиями.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        """
        response = await ac.delete("/api/tweets/3/follow", headers={"api-key": "test"})
        good_response_test(response)

    @classmethod
    async def test_check_unfollow_user_in_db(cls, async_session: AsyncSession) -> None:
        """
        Проверяет, что подписка была успешно удалена из базы данных.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных
        """
        record1, record2, record3 = await cls.check_followers_for_existence(
            async_session
        )
        assert all([record1, record2]) and record3 is False

    @classmethod
    async def test_check_unfollow_user_on_page(cls, ac: AsyncClient) -> None:
        """
        После отказа от подписки делает запрос на получение информации о пользователе,
        который сделал этот запрос.
        Проверяет, что статус код ответа от сервера равен 200, и тело ответа совпадает с ожиданиями.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        """
        cls.user1_info["user"]["following"].pop(-1)
        await cls.test_get_me_info(ac)

    @classmethod
    async def test_get_profile_info(cls, ac: AsyncClient) -> None:
        """
        Делает запрос на получение информации о пользователе с id 2.
        Проверяет, что статус код ответа от сервера равен 200, и тело ответа совпадает с ожиданиями.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        """
        response = await ac.get("/api/users/2")
        assert response.status_code == 200
        assert response.json() == PROFILE_DATA

    @classmethod
    @pytest.mark.parametrize(
        "data", get_data_from_fixtures("users_authenticated_error.json")
    )
    async def test_authenticated_error(
        cls, ac: AsyncClient, data: list[str, str]
    ) -> None:
        """
        Делает запросы на получение информации, подписку, отписку.
        Но предоставляет токен с несуществующим пользователем.

        Проверяет, что статус код ответа от сервера равен 401,
        и операция не была выполнена успешно из-за непройденной авторизации.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        data: Список с адресом ресурса и методом http-запроса
        """
        url, method = data
        response = await ac.request(
            method=method, url=url, headers={"api-key": BAD_TOKEN}
        )
        authorization_error_test(response)

    @classmethod
    @pytest.mark.parametrize(
        "data", get_data_from_fixtures("users_request_validation_error.json")
    )
    async def test_request_validation_error(
        cls, ac: AsyncClient, data: list[str, str, dict | None]
    ) -> None:
        """
        Делает запросы на различные ресурсы с невалидными данными.

        Проверяет, что статус код ответа от сервера равен 422,
        и операция не была выполнена успешно.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        data: Список с адресом ресурса, методом http-запроса и json - данными, если они есть
        """
        url, method, json_data = data
        response = await ac.request(
            url=url, method=method, headers={"api-key": "test"}, json=json_data
        )
        request_validation_error_test(response)

    @classmethod
    @pytest.mark.parametrize(
        "data", get_data_from_fixtures("users_not_found_error.json")
    )
    async def test_not_found_error(cls, ac: AsyncClient, data: list[str, str]) -> None:
        """
        Делает запросы на различные ресурсы, которых не существует на сервере.

        Проверяет, что статус код ответа от сервера равен 404,
        и операция не была выполнена успешно.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        data: Список с адресом ресурса, и методом http-запроса
        """
        url, method = data
        response = await ac.request(method=method, url=url, headers={"api-key": "test"})
        not_found_error_test(response)


class TestTweets:
    """
    Класс с тестами, нацеленными на взаимодействие с твитами в базе данных, контроллере.
    """

    all_tweets = copy.deepcopy(ALL_TWEETS)

    @classmethod
    async def check_tweets_for_existence(
        cls, async_session: AsyncSession
    ) -> list[bool]:
        """
        Получает данные из базы о твитах по различным параметрам.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных

        Возвращает список из трех значений. Каждое принимает True или False.
        Если значение принимает True, то твит найден в базе даннных. Иначе не найден.
        """

        return await check_objects_for_existence(
            repository=TweetRepository, session=async_session, objects=TWEETS
        )

    @classmethod
    async def check_likes_for_existence(cls, async_session: AsyncSession) -> list[bool]:
        """
        Получает данные из базы о лайках по различным параметрам.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных

        Возвращает список из трех значений. Каждое принимает True или False.
        Если значение принимает True, то твит найден в базе даннных. Иначе не найден.
        """
        return await check_objects_for_existence(
            repository=LikeRepository, session=async_session, objects=LIKES
        )

    @classmethod
    async def test_no_tweets_in_db(cls, async_session: AsyncSession) -> None:
        """
        Проверяет, что в базе данных нет твитов.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных
        """
        assert not any(await cls.check_tweets_for_existence(async_session))

    @classmethod
    async def test_get_all_tweets(cls, ac: AsyncClient) -> None:
        """
        Делает запрос на получение всех твитов.
        Проверяет, что статус код ответа от сервера равен 200, и тело ответа совпадает с ожиданиями.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        """
        response = await ac.get("/api/tweets", headers={"api-key": "test"})
        assert response.status_code == 200
        assert response.json() == cls.all_tweets

    @classmethod
    @pytest.mark.parametrize("data", get_data_from_fixtures("create_tweets.json"))
    async def test_create_tweets_endpoint(
        cls,
        ac: AsyncClient,
        async_session: AsyncSession,
        data: list[str, dict, int],
    ) -> None:
        """
        Делает запросы на создание твитов.
        Проверяет, что статус код ответа от сервера равен 201, и тело ответа совпадает с ожиданиями.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        async_session: Сессия для асинхронной работы с базой данных
        data: Список с токеном пользователя, делающего запрос, данными твита и его идентификатором,
        который должен вернуться в ответе

        """
        token, json_data, tweet_id = data
        response = await ac.post(
            "api/tweets", headers={"api-key": token}, json=json_data
        )
        assert response.status_code == 201
        assert response.json() == {"result": True, "tweet_id": tweet_id}

    @classmethod
    async def test_check_tweets_in_db(cls, async_session: AsyncSession) -> None:
        """
        Проверяет, что все твиты сохранились в базе данных.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных
        """
        assert all(await cls.check_tweets_for_existence(async_session))

    @classmethod
    async def test_check_tweets_on_page(cls, ac: AsyncClient) -> None:
        """
        После сохранения твитов делает запрос на получение этих твитов.
        Проверяет, что статус код ответа от сервера равен 200, и тело ответа совпадает с ожиданиями.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        """
        tweets = cls.all_tweets["tweets"]
        tweets.extend(ADDED_TWEETS)
        await cls.test_get_all_tweets(ac)

    @classmethod
    async def test_no_likes_in_db(cls, async_session: AsyncSession) -> None:
        """
        Проверяет, что в базе данных нет лайков.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных
        """
        assert not any(await cls.check_likes_for_existence(async_session))

    @classmethod
    @pytest.mark.parametrize("data", get_data_from_fixtures("like_tweet.json"))
    async def test_like_tweet_endpoint(cls, ac: AsyncClient, data: list[str, str]):
        """
        Делает запросы на проставление лайков твитам.
        Проверяет, что статус код ответа от сервера равен 200, и тело ответа совпадает с ожиданиями.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        data: Список с адресом ресурса и токеном пользователя, делающего запрос

        """
        url, token = data
        response = await ac.post(url, headers={"api-key": token})
        good_response_test(response)

    @classmethod
    async def test_check_likes_in_db(cls, async_session: AsyncSession) -> None:
        """
        Проверяет, все лайки твитам сохранились в базе данных.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных
        """
        assert all(await cls.check_likes_for_existence(async_session))

    @classmethod
    async def test_check_likes_on_page(cls, ac: AsyncClient) -> None:
        """
        После сохранения лайков твитам делает запрос на получение твитов.
        Проверяет, что статус код ответа от сервера равен 200, и тело ответа совпадает с ожиданиями.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        """
        tweets = cls.all_tweets["tweets"]
        tweets[2]["likes"].extend(ADDED_LIKES)
        tweets[1]["likes"].append(LIKE)
        tweets[2], tweets[0] = tweets[0], tweets[2]

        await cls.test_get_all_tweets(ac)

    @classmethod
    async def test_delete_like_tweet_endpoint(cls, ac: AsyncClient) -> None:
        """
        Делает запрос на удаление лайка у твита.
        Проверяет, что статус код ответа от сервера равен 200, и тело ответа совпадает с ожиданиями.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        """
        response = await ac.delete("api/tweets/2/likes", headers={"api-key": "test3"})
        good_response_test(response)

    @classmethod
    async def test_check_deleted_like_tweet_in_db(
        cls, async_session: AsyncSession
    ) -> None:
        """
        Проверяет, что лайк твиту удалился из базы данных.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных
        """
        record1, record2, record3 = await cls.check_likes_for_existence(async_session)
        assert all((record1, record2)) and record3 is False

    @classmethod
    async def test_check_deleted_like_tweet_on_page(cls, ac: AsyncClient) -> None:
        """
        После удаления лайка твиту делает запрос на получение твитов.
        Проверяет, что статус код ответа от сервера равен 200, и тело ответа совпадает с ожиданиями.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        """
        tweets = cls.all_tweets["tweets"]
        tweets[1]["likes"].pop(0)
        tweets[1], tweets[2] = tweets[2], tweets[1]
        await cls.test_get_all_tweets(ac)

    @classmethod
    async def test_delete_tweet_endpoint(cls, ac: AsyncClient) -> None:
        """
        Делает запрос на удаление твита.
        Проверяет, что статус код ответа от сервера равен 200, и тело ответа совпадает с ожиданиями.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        """
        response = await ac.delete("api/tweets/2", headers={"api-key": "test"})
        good_response_test(response)

    @classmethod
    async def test_check_deleted_tweet_in_db(cls, async_session: AsyncSession) -> None:
        """
        Проверяет, что твит удалился из базы данных.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных
        """
        record1, record2, record3 = await cls.check_tweets_for_existence(async_session)
        assert all((record1, record3)) and record2 is False

    @classmethod
    async def test_check_deleted_tweet_on_page(cls, ac: AsyncClient) -> None:
        """
        После удаления твита делает запрос на получение твитов.
        Проверяет, что статус код ответа от сервера равен 200, и тело ответа совпадает с ожиданиями.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        """
        cls.all_tweets["tweets"].pop(-1)
        await cls.test_get_all_tweets(ac)

    @classmethod
    @pytest.mark.parametrize(
        "data", get_data_from_fixtures("tweets_authenticated_error.json")
    )
    async def test_authenticated_error(
        cls, ac: AsyncClient, data: list[str, str]
    ) -> None:
        """
        Делает запросы на создание твита, получение, проставления лайка и удаления лайка.
        Но предоставляет токен с несуществующим пользователем.

        Проверяет, что статус код ответа от сервера равен 401,
        и операция не была выполнена успешно из-за непройденной авторизации.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        data: Список с адресом ресурса, и методом http-запроса
        """
        url, method = data
        response = await ac.request(
            method=method, url=url, headers={"api-key": BAD_TOKEN}
        )
        authorization_error_test(response)

    @classmethod
    @pytest.mark.parametrize(
        "data", get_data_from_fixtures("tweets_request_validation_error.json")
    )
    async def test_request_validation_error(
        cls, ac: AsyncClient, data: list[str, str, Any]
    ) -> None:
        """
        Делает запросы на различные ресурсы с невалидными данными.

        Проверяет, что статус код ответа от сервера равен 422,
        и операция не была выполнена успешно.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        data: Список с адресом ресурса, методом http-запроса и данными, если они есть
        """
        url, method, json_data = data
        response = await ac.request(
            method=method, url=url, headers={"api-key": "test"}, json=json_data
        )
        request_validation_error_test(response)

    @classmethod
    @pytest.mark.parametrize(
        "data", get_data_from_fixtures("tweets_not_found_error.json")
    )
    async def test_not_found_error(cls, ac: AsyncClient, data: list[str, str]) -> None:
        """
        Делает запросы на различные ресурсы, которых не существует на сервере.

        Проверяет, что статус код ответа от сервера равен 404,
        и операция не была выполнена успешно.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        data: Список с адресом ресурса, и методом http-запроса
        """
        url, method = data
        response = await ac.request(method=method, url=url, headers={"api-key": "test"})
        not_found_error_test(response)


class TestMedia:
    @classmethod
    async def check_media_for_existence(cls, async_session: AsyncSession) -> bool:
        """
        Получает данные из базы о картинке по параметрам.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных

        Возвращает True или False.
        Если значение принимает True, то картинка найдена в базе даннных. Иначе не найдена.
        """
        medias = await check_objects_for_existence(
            repository=MediaRepository, session=async_session, objects=[{"id": 1}]
        )
        return medias[0]

    @classmethod
    async def link_media_to_tweet(cls, async_session: AsyncSession) -> None:
        """
        Связывает картинку и твит на стороне базе данных.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных
        """
        await TweetMediaRepository.create_object(
            session=async_session, data={"tweet_id": 1, "media_id": 1}
        )

    @classmethod
    async def make_request_on_media_endpoint(
        cls, ac: AsyncClient, filename: str
    ) -> Response | None:
        """
        Делает запрос на создание картинки.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        filename: Название файла

        Возвращает ответ от сервера
        """
        if not filename:
            return await ac.post("api/medias")
        with open(f"files/{filename}", mode="rb") as file:
            files = {"file": (filename, file)}
            return await ac.post("api/medias", headers={"api-key": "test"}, files=files)

    @classmethod
    async def test_no_media_in_db(cls, async_session: AsyncSession) -> None:
        """
        Проверяет, что картинок нет в базе данных.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных
        """
        assert await cls.check_media_for_existence(async_session) is False

    @classmethod
    def test_check_no_media_on_server(cls) -> None:
        """
        Проверяет, что картинок нет на сервере.
        """
        assert len(listdir("src/upload_files")) == 0

    @classmethod
    async def test_create_media_endpoint(cls, ac: AsyncClient) -> None:
        """
        Делает запрос на создание картинки.
        Проверяет, что статус код ответа от сервера равен 201, и тело ответа совпадает с ожиданиями.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        """
        response = await cls.make_request_on_media_endpoint(ac, filename="FastAPI.png")
        assert response.status_code == 201
        assert response.json() == {"result": True, "media_id": 1}

    @classmethod
    async def test_check_media_in_db(cls, async_session: AsyncSession) -> None:
        """
        Проверяет, что картинка сохранена в базе.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных
        """
        assert await cls.check_media_for_existence(async_session) is True

    @classmethod
    def test_check_media_on_server(cls) -> None:
        """
        Проверяет, что картинка сохранена на сервере,
        и разница между созданием картинки и проведением теста отличается не более, чем на 2 секунды.
        """
        files = listdir("src/upload_files/1")
        datetime_now = datetime.utcnow()
        assert len(files) == 1
        assert files[0].endswith("FastAPI.png")
        existing_file = files[0][: -len("_FastAPI.png")]
        file_creation_datetime = datetime.strptime(
            existing_file, "%Y-%m-%dT%H:%M:%S.%f"
        )
        assert (datetime_now - file_creation_datetime).total_seconds() < 2

    @classmethod
    async def test_check_media_on_page(
        cls, ac: AsyncClient, async_session: AsyncSession
    ) -> None:
        """
        После сохранения картинки делает запрос на получение твитов.
        Проверяет, что статус код ответа от сервера равен 200, и тело ответа совпадает с ожиданиями.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        async_session: Сессия для асинхронной работы с базой данных
        """
        await cls.link_media_to_tweet(async_session)
        tweets = TestTweets.all_tweets["tweets"]
        filename = listdir("src/upload_files/1")[0]
        tweets[0]["attachments"].append(rf"upload_files/1/{filename}")
        await TestTweets.test_get_all_tweets(ac)

    @classmethod
    async def test_delete_tweet_with_media(
        cls, ac: AsyncClient, async_session: AsyncSession
    ) -> None:
        """
        Делает запрос на удаление твита.
        Производит несколько проверок:
        1) Статус код ответа от сервера равен 200, и тело ответа совпадает с ожиданиями.
        2) Картинка удалилась из базы данных
        3) Картинка удалилась на сервере

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        async_session: Сессия для асинхронной работы с базой данных
        """
        response = await ac.delete("api/tweets/1", headers={"api-key": "test"})
        good_response_test(response)
        await cls.test_no_media_in_db(async_session)
        assert len(listdir("src/upload_files/1")) == 0

    @classmethod
    @pytest.mark.parametrize(
        "filename", get_data_from_fixtures("media_request_validation_error.json")
    )
    async def test_request_validation_error(
        cls, ac: AsyncClient, filename: str
    ) -> None:
        """
        Делает запросы на добавление картинок с невалидными расширениями файлов.

        Проверяет, что статус код ответа от сервера равен 422,
        и операция не была выполнена успешно.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        filename: Название файла

        """
        response = await cls.make_request_on_media_endpoint(ac, filename=filename)
        request_validation_error_test(response)


class TestGeneric:
    """
    Класс с общими тестами, нацеленными на проверку целостности данных в базе и корректности работы контроллеров.
    """

    @classmethod
    async def test_check_users_in_db(cls, async_session: AsyncSession) -> None:
        """
        Проверяет, что невалидные данные при взаимодействии с пользователями в запросах не попали в базу данных
        и не изменили ее состояния.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных
        """
        await TestUsers.test_check_users_in_db(async_session)
        assert await UserRepository.count_number_objects(async_session) == 4

    @classmethod
    async def test_followers_in_db(cls, async_session: AsyncSession) -> None:
        """
        Проверяет, что невалидные данные при взаимодействии с подпиской и отпиской в запросах не попали в базу данных
        и не изменили ее состояния.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных
        """
        await TestUsers.test_check_unfollow_user_in_db(async_session)
        assert await UserFollowerRepository.count_number_objects(async_session) == 2

    @classmethod
    async def test_check_tweets_in_db(cls, async_session: AsyncSession) -> None:
        """
        Проверяет, что невалидные данные при взаимодействии с твитами в запросах не попали в базу данных
        и не изменили ее состояния.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных
        """
        tweets = await TestTweets.check_tweets_for_existence(async_session)
        assert (not any(tweets[:2])) and tweets[2] is True
        assert await TweetRepository.count_number_objects(async_session) == 1

    @classmethod
    async def test_check_likes_in_db(cls, async_session: AsyncSession) -> None:
        """
        Проверяет, что невалидные данные при взаимодействии с лайками твитов в запросах не попали в базу данных
        и не изменили ее состояния.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных
        """
        assert await LikeRepository.count_number_objects(async_session) == 0

    @classmethod
    async def test_check_medias_in_db(cls, async_session: AsyncSession) -> None:
        """
        Проверяет, что невалидные данные при взаимодействии с картинками в запросах не попали в базу данных
        и не изменили ее состояния.

        Параметры:

        async_session: Сессия для асинхронной работы с базой данных
        """
        assert await MediaRepository.count_number_objects(async_session) == 0
        assert await TweetMediaRepository.count_number_objects(async_session) == 0

    @classmethod
    async def test_not_found_page(cls, ac: AsyncClient) -> None:
        """
        Делает запрос на несуществующий ресурс.
        Проверяет, что статус код ответа от сервера равен 404,
        и операция не была выполнена успешно.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        """
        response = await ac.get("/")
        not_found_error_test(response)

    @classmethod
    async def test_method_not_allowed(cls, ac: AsyncClient) -> None:
        """
        Делает запрос на ресурс с http-методом, который не предусмотрен этим ресурсом.
        Проверяет, что статус код ответа от сервера равен 405,
        и операция не была выполнена успешно.

        Параметры:

        ac: Клиент для асинхронного взаимодействия с приложением
        """
        response = await ac.delete("api/users")
        assert response.status_code == 405
        assert response.json() == METHOD_NOT_ALLOWED
