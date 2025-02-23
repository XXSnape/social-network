"""
Модуль с сервисами, управляющими медиа.
"""

import os
from datetime import datetime

import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.errors import PICTURE_NOT_CREATED_ERROR
from src.exceptions.request_exceptions import INCORRECT_FILE_EXTENSION_EXCEPTION
from src.repositories.medias import MediaRepository


class MediaService:
    """
    Сервис по работе с медиа.
    """

    @classmethod
    async def save_file_to_disk(cls, file: UploadFile, user_id: int) -> str:
        """
        Сохраняет пользовательский файл на сервер в директории user_id.

        Параметры:

        file: Файл с картинкой
        user_id: Идентификатор пользователя

        Возвращает название файла со случайной строкой, которое было сохранено на сервере.
        """
        current_datetime_utc = datetime.utcnow()
        file_creation_datetime = current_datetime_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")
        try:
            os.mkdir(f"src/upload_files/{user_id}")
        except FileExistsError:
            pass
        path_to_file = (
            f"upload_files/{user_id}/{file_creation_datetime}_{file.filename}"
        )
        async with aiofiles.open(f"src/{path_to_file}", mode="wb") as output_file:
            content = await file.read()
            await output_file.write(content)
        return path_to_file

    @classmethod
    async def save_media(
        cls, session: AsyncSession, file: UploadFile, user_id: int
    ) -> dict[str, bool | int]:
        """
        Сохраняет файл в базу данных.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        file: Файл с картинкой
        user_id: Идентификатор пользователя

        Возвращает словарь с id добавленной картинки и статусом операции.
        """
        if not any(
            file.filename.endswith(extension)
            for extension in ("png", "jpg", "jpeg", "webp")
        ):
            raise INCORRECT_FILE_EXTENSION_EXCEPTION
        filename = await cls.save_file_to_disk(file=file, user_id=user_id)
        media_id = await MediaRepository.create_object(
            session=session,
            data={"attachment": filename},
            exception_detail=PICTURE_NOT_CREATED_ERROR,
        )
        return {"result": True, "media_id": media_id}

    @classmethod
    async def delete_media_from_disk_by_tweet_id(
        cls, session: AsyncSession, tweet_id: int
    ) -> None:
        """
        Удаляет файлы с сервера.

        Параметры:

        session: Сессия для асинхронной работы с базой данных
        tweet_id: Идентификатор твита, у которого нужно удалить картинки
        """
        paths = await MediaRepository.delete_media_and_return_attachments(
            session=session, tweet_id=tweet_id
        )
        for path in paths:
            os.remove(f"src/{path}")
