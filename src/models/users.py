"""
Модуль с моделями пользователя.
"""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .tweets import TweetModel


class UserModel(Base):
    """
    Модель пользователя.
    """

    name: Mapped[str]  # Имя пользователя
    token: Mapped[str] = mapped_column(
        unique=True
    )  # Токен пользователя. Является хэшем.
    # Должен быть уникальным для идентификации
    tweets: Mapped[list["TweetModel"]] = relationship(
        back_populates="author"
    )  # Твиты, принадлежащие пользователю

    followers: Mapped[list["UserModel"]] = relationship(
        back_populates="following",
        secondary="followers",
        primaryjoin="UserModel.id == FollowerModel.user_id",
        secondaryjoin="UserModel.id == FollowerModel.follower_id",
    )  # Подписчики пользователя
    following: Mapped[list["UserModel"]] = relationship(
        back_populates="followers",
        secondary="followers",
        primaryjoin="UserModel.id == FollowerModel.follower_id",
        secondaryjoin="UserModel.id == FollowerModel.user_id",
    ) # Пользователи, на которых подписан текущий


class FollowerModel(Base):
    """
    Модель подписчика на пользователя.
    """

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "follower_id",
            name="idx_uniq_user_follower",
        ),
    )  # Ограничения на уникальность записей.
    # Чтобы один пользователь не мог подписаться более одного раза на другого пользователя
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        )
    )  # Внешний ключ на пользователя
    follower_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        )
    )  # Внешний ключ на подписчика
