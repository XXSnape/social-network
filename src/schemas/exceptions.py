"""
Модуль со схемами кастомных исключений.
"""

from pydantic import BaseModel


class ExceptionSchema(BaseModel):
    """
    Схема, отображающаяся пользователю при любых ошибках.
    """

    result: bool = False
    error_type: str
    error_messages: str
