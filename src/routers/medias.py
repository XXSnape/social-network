"""
Модуль с контроллерами картинок.
"""

from fastapi import APIRouter, Depends, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db_helper import db_helper
from src.dependencies.users import get_user
from src.services.media_service import MediaService

router = APIRouter(prefix="/medias", tags=["Medias"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def get_file_from_tweet(
    file: UploadFile,
    session: AsyncSession = Depends(db_helper.get_async_session),
    user=Depends(get_user),
) -> dict[str, bool | int]:
    """
    Сохраняет картинку в базу данных.

    Параметры:

    file: Файл с картинкой
    session: Сессия для асинхронной работы с базой данных
    user: Пользователь, отправивший запрос

    Возвращает словарь с id добавленной картинки и статусом операции.
    """
    return await MediaService.save_media(session=session, file=file, user_id=user.id)
