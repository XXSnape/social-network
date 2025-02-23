"""
Модуль с общими схемами.
"""

from pydantic import BaseModel


class ResultSchema(BaseModel):
    """
    Схема, отображающаяся пользователю после совершения операций.
    """

    result: bool
