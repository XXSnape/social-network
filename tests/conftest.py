"""
Модуль с настройками для тестов.
"""

import shutil
from os import mkdir
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.db_helper import db_helper
from src.core.settings import settings
from src.main import app

engine = create_async_engine(settings.db.database_url, poolclass=NullPool)
async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, autoflush=False
)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Генерирует сессию для асинхронного взаимодействия с тестовой базой данных внутри приложения.
    """
    async with async_session_maker() as session:  # type: AsyncSession
        yield session


@pytest.fixture()
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Генерирует сессию для асинхронного взаимодействия с тестовой базой данных внутри тестов.
    """
    async with async_session_maker() as session:  # type: AsyncSession
        yield session


@pytest.fixture(autouse=True, scope="session")
def create_directory_for_media() -> None:
    """
    Создает директорию src/upload_files внутри приложения для тестов с картинками.
    После завершения всех тестов удаляет директорию со всем содержимым.
    """
    mkdir("src/upload_files")
    yield
    shutil.rmtree("src/upload_files")


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    """
    Возвращает клиента для асинхронного взаимодействия с приложением внутри тестов.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


app.dependency_overrides[db_helper.get_async_session] = override_get_async_session
