"""
Модуль со схемами пользователей.
"""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from .generic import ResultSchema


class UserInfoSchema(BaseModel):
    """
    Схема пользователя.
    """

    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class UserInSchema(BaseModel):
    """
    Схема для фильтрации данных при создании пользователя.
    """

    name: Annotated[str, Field(min_length=1, max_length=100)]
    token: Annotated[str, Field(min_length=1, max_length=100)]
    model_config = ConfigDict(extra="forbid")


class UserOutputSchema(UserInfoSchema):
    """
    Вложенная схема, возвращающаяся при предоставлении данных о пользователе.
    """

    followers: list[UserInfoSchema]
    following: list[UserInfoSchema]


class UserSchema(UserInfoSchema):
    """
    Схема пользователя со всеми его данными.
    """

    token: str


class UserCreatedSchema(ResultSchema):
    """
    Схема, возвращающаяся после создания пользователя.
    """

    id: int
    name: str


class UserProfileSchema(ResultSchema):
    """
    Схема, возвращающаяся при предоставлении данных о профиле пользователя.
    """

    user: UserOutputSchema


class LikeSchema(BaseModel):
    """
    Схема лайка.
    """

    user_id: Annotated[int, Field(validation_alias="id")]
    name: str
