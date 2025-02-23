"""
Модуль с типами для параметров пути
"""

from typing import Annotated, TypeAlias

from fastapi import Path

FromOneToMlnPath: TypeAlias = Annotated[int, Path(ge=1, le=10**6)]
