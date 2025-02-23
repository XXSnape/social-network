"""
Модуль для работы с таблицей лайков.
"""

from src.models import LikeModel

from .repository import ManagerRepository


class LikeRepository(ManagerRepository):
    """
    Класс - репозиторий для работы с таблицей лайков.
    """

    model = LikeModel
