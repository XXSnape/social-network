"""
Модуль для работы с базой данных.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .settings import settings


class DBHelper:
    """
    Класс - помощник для работы с базой данных.
    """

    def __init__(self, url: str, echo: bool = False) -> None:
        """
        Инициализация класса.

        Параметры:
        url: Строка для подключения к базе данных
        echo: Принимает значения True или False

        Если установлен в True, то в консоль будут выводиться запросы к базе. По умолчанию False.
        """
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )  # Двигатель для работы с асинхронной базой данных
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autocommit=False,
            expire_on_commit=False,
        )  # Фабрика сессий для работы с асинхронной базой данных

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Возвращает сессию для асинхронной работы с базой данных.
        """
        async with self.session_factory() as session:  # type: AsyncSession
            yield session
            await session.close()


db_helper = DBHelper(
    url=settings.db.database_url,
    echo=settings.db.echo,
)
