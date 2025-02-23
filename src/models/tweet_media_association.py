"""
Модуль с моделями, связывающими твит и медиа.
"""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TweetMediaAssociation(Base):
    """
    Модель для связи твита и картинки.
    """

    __tablename__ = "tweet_media_association"
    tweet_id: Mapped[int] = mapped_column(
        ForeignKey(
            "tweets.id",
            ondelete="CASCADE",
        ),
    )  # Внешний ключ на твит
    media_id: Mapped[int] = mapped_column(
        ForeignKey(
            "medias.id",
            ondelete="CASCADE",
        ),
        unique=True,
    )  # Внешний ключ на картинку. Одна картинка может быть прикреплена только к одному твиту
