"""
Модуль со схемами твитов.
"""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_serializer

from .generic import ResultSchema
from .users import LikeSchema, UserInfoSchema


class TweetInSchema(BaseModel):
    """
    Схема для фильтрации пользовательский данных при создании твита.
    """

    tweet_data: Annotated[str, Field(min_length=1)]
    tweet_media_ids: Annotated[list[PositiveInt], Field(default_factory=list)]
    model_config = ConfigDict(extra="forbid")


class TweetInResultSchema(ResultSchema):
    """
    Схема, возвращающаяся пользователю после создания твита.
    """

    tweet_id: int


class AttachmentSchema(BaseModel):
    attachment: str


class TweetContentSchema(BaseModel):
    """
    Вложенная схема, возвращающаяся при предоставлении данных о твитах.
    """

    id: int
    content: str
    attachments: list[AttachmentSchema]
    author: UserInfoSchema
    likes: list[LikeSchema]

    @field_serializer("attachments")
    def list_of_attachments(self, attachments: list[AttachmentSchema]) -> list[str]:
        """
        Возвращает пути к картинкам в виде списка строк
        """
        return [attach.attachment for attach in attachments]


class TweetsOutputSchema(ResultSchema):
    """
    Схема, возвращающаяся при предоставлении данных о твитах.
    """

    tweets: list[TweetContentSchema]
