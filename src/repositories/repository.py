"""
Модуль с абстрактными репозиториями для работы с таблицами базы данных.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from sqlalchemy import delete, func, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.errors import OBJECT_NOT_CREATED_ERROR, OBJECT_NOT_FOUND_ERROR


class AbstractRepository(ABC):
    """
    Абстрактный класс - репозиторий.
    """

    @abstractmethod
    async def create_object(
        self,
        session: AsyncSession,
        data: dict,
        exception_detail: str = OBJECT_NOT_CREATED_ERROR,
        exception_foreign_constraint_detail: str = OBJECT_NOT_FOUND_ERROR,
        commit_need: bool = True,
    ) -> int:
        """
        Добавляет новый объект в базу данных.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        data: Словарь с данными, которые должны быть добавлены в базу

        exception_detail: Сообщение об ошибке, которое возникает во всех случаях,
        когда не удается создать объект

        exception_foreign_constraint_detail: Сообщение об ошибке,
        которое возникает из-за ограничений внешнего ключа

        commit_need: Принимает значения True или False.
        Если установлен в True, то изменения будут сохранены в базе. По умолчанию True.

        Возвращает идентификатор добавленной записи.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_object_by_params(
        self,
        session: AsyncSession,
        data: dict,
        exception_detail: str = OBJECT_NOT_FOUND_ERROR,
        commit_need=True,
    ) -> bool:
        """
        Удаляет объекты из базы данных.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        data: Словарь с данными, по которым будет осуществлен поиск объектов для удаления

        exception_detail: Сообщение об ошибке, которое возникает в случаях, когда объект не был удален

        commit_need: Принимает значения True или False.
        Если установлен в True, то изменения будут сохранены в базе. По умолчанию True.

        Возвращает True, если объекты были удалены и False в противном случае.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_object_by_params(
        self, session: AsyncSession, data: dict
    ) -> Optional[Any]:
        """
        Ищет объект в базе данных.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        data: Словарь с данными, по которым будет осуществлен поиск объекта

        Возвращает объект базы данных или None.
        """
        raise NotImplementedError

    @abstractmethod
    async def check_exists_object_by_params(
        self, session: AsyncSession, data: dict
    ) -> bool:
        """
        Ищет объект в базе данных.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        data: Словарь с данными, по которым будет осуществлен поиск объекта

        Возвращает True, если объект существует, и False в противном случае.
        """
        raise NotImplementedError

    @abstractmethod
    async def count_number_objects(self, session: AsyncSession) -> int:
        """
        Считает количество записей в таблице.

        Параметры:

        session: Сессия для асинхронной работы с базой данных

        Возвращает количество записей в таблице.
        """
        raise NotImplementedError


class ManagerRepository(AbstractRepository):
    """
    Класс - репозиторий, реализующий все методы абстрактного класса.
    """

    model = None  # Модель базы данных

    @classmethod
    async def create_object(
        cls,
        session: AsyncSession,
        data: dict,
        exception_detail: str = OBJECT_NOT_CREATED_ERROR,
        exception_foreign_constraint_detail: str = OBJECT_NOT_FOUND_ERROR,
        commit_need: bool = True,
    ) -> int:
        """
        Добавляет новый объект в базу данных.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        data: Словарь с данными, которые должны быть добавлены в базу

        exception_detail: Сообщение об ошибке, которое возникает во всех случаях,
        когда не удается создать объект

        exception_foreign_constraint_detail: Сообщение об ошибке,
        которое возникает из-за ограничений внешнего ключа

        commit_need: Принимает значения True или False.
        Если установлен в True, то изменения будут сохранены в базе. По умолчанию True.

        Возвращает идентификатор добавленной записи.
        """
        stmt = insert(cls.model).values(**data).returning(cls.model.id)
        try:
            result = await session.execute(stmt)
            if commit_need:
                await session.commit()
            return result.scalar_one()

        except IntegrityError as err:
            await session.rollback()
            if "foreign key constraint" in err.args[0]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=exception_foreign_constraint_detail,
                )
            raise RequestValidationError(errors=exception_detail)

    @classmethod
    async def delete_object_by_params(
        cls,
        session: AsyncSession,
        data: dict,
        exception_detail: str = OBJECT_NOT_FOUND_ERROR,
        commit_need=True,
    ) -> bool:
        """
        Удаляет объекты из базы данных.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        data: Словарь с данными, по которым будет осуществлен поиск объектов для удаления

        exception_detail: Сообщение об ошибке, которое возникает в случаях, когда объект не был удален

        commit_need: Принимает значения True или False.
        Если установлен в True, то изменения будут сохранены в базе. По умолчанию True.

        Возвращает True, если объекты были удалены и False в противном случае.
        """
        stmt = delete(cls.model).filter_by(**data).returning(cls.model.id)
        result = await session.execute(stmt)
        result = bool(result.fetchone())
        if result is False:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=exception_detail
            )
        if commit_need:
            await session.commit()
        return result

    @classmethod
    async def get_object_by_params(
        cls, session: AsyncSession, data: dict
    ) -> Optional[model]:
        """
        Ищет объект в базе данных.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        data: Словарь с данными, по которым будет осуществлен поиск объекта

        Возвращает объект базы данных или None.
        """
        query = select(cls.model).filter_by(**data)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def check_exists_object_by_params(
        cls, session: AsyncSession, data: dict
    ) -> bool:
        """
        Ищет объект в базе данных.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        data: Словарь с данными, по которым будет осуществлен поиск объекта

        Возвращает True, если объект существует, и False в противном случае.
        """
        query = select(cls.model.id).filter_by(**data).limit(1)
        result = await session.scalar(query)
        return bool(result)

    @classmethod
    async def count_number_objects(cls, session: AsyncSession) -> int:
        """
        Считает количество записей в таблице.

        Параметры:

        session: Сессия для асинхронной работы с базой данных

        Возвращает количество записей в таблице.
        """
        query = select(func.count(cls.model.id))
        return await session.scalar(query)
