"""
Модуль с моделями твита.
"""

from typing import TYPE_CHECKING

from sqlalchemy import TEXT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .media import MediaModel
    from .users import UserModel


class TweetModel(Base):
    """
    Модель твита.
    """

    content: Mapped[str] = mapped_column(TEXT)  # Информация, содержащаяся в твите
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )  # Внешний ключ на автора твита

    attachments: Mapped[list["MediaModel"]] = relationship(
        back_populates="tweet",
        secondary="tweet_media_association",
    )  # Картинки, относящиеся к твиту

    author: Mapped["UserModel"] = relationship(
        back_populates="tweets",
    )  # Автор твита

    likes: Mapped[list["UserModel"]] = relationship(
        secondary="likes",
    )  # Лайки твита
