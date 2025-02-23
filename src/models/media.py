"""
Модуль с медиа - моделями.
"""

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from .base import Base

if TYPE_CHECKING:
    from .tweets import TweetModel


class MediaModel(Base):
    """
    Модель картинки.
    """

    attachment: Mapped[str]  # Путь к картинке
    tweet: Mapped["TweetModel"] = relationship(
        back_populates="attachments",
        secondary="tweet_media_association",
    )  # Твит, на который установлена эта картинка
