"""
Модуль для работы с таблицей, связывающей твиты и картинки.
"""

from src.models import TweetMediaAssociation

from .repository import ManagerRepository


class TweetMediaRepository(ManagerRepository):
    """
    Класс - репозиторий для работы с таблицей, связывающей твиты и картинки.
    """

    model = TweetMediaAssociation
