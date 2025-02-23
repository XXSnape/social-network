"""
Модуль с типами для параметров запроса
"""

from typing import Annotated, TypeAlias

from fastapi import Query

FromOneToMlnQuery: TypeAlias = Annotated[int | None, Query(ge=1, le=10**6)]
