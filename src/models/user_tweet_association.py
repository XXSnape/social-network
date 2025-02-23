"""
Модуль с моделями, связывающими твит и пользователя.
"""

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class LikeModel(Base):
    """
    Модель лайка.
    """

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "tweet_id",
            name="idx_uniq_user_tweet",
        ),
    )  # Ограничения на уникальность записей. Чтобы один пользователь не мог поставить более одного лайка твиту
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        )
    )  # Внешний ключ на пользователя
    tweet_id: Mapped[int] = mapped_column(
        ForeignKey(
            "tweets.id",
            ondelete="CASCADE",
        )
    )  # Внешний ключ на твит
