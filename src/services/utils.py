"""
Модуль с полезными функциями.
"""

from hashlib import sha256
from typing import Sequence


def get_hash_token(token: str) -> str:
    """
    Хэширует входящий токен.

    Параметры:

    token: Токен пользователя

    Возвращает захэшированную строку.
    """
    return sha256(token.encode("utf-8")).hexdigest()


def handle_errors(errors: Sequence | str) -> str:
    """
    Обрабатывает ошибки.

    Параметры:

    errors: Строка или последовательность, содержащая информацию об ошибках

    Возвращает строку со всеми ошибками.
    """
    if isinstance(errors, str):
        error_messages = errors
    else:
        for index, item in enumerate(errors):
            if "url" in item:
                item.pop("url")
        count = 1
        error_messages = ""
        for error in errors:
            error_messages += (
                f"{count}): "
                f"Type: {error.get('type', 'unknown')}. "
                f"Msg: {error.get('type', 'msg')}. "
                f"Error: {error.get('ctx', {}).get('error', 'unknown')}. "
            )
    return error_messages
