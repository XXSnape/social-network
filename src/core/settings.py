"""
Модуль для работы с настройками виртуального окружения.
"""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class DBSettings(BaseSettings):
    """
    Класс для настройки параметров подключения к базе данных.
    """

    DB_HOST: str
    DB_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    echo: bool = False

    @property
    def database_url(self) -> str:
        """
        Возвращает строку для подключения к базе данных.
        """
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"
        )


class Settings(BaseSettings):
    """
    Класс для настройки виртуального окружения из файла .env.
    """

    db: DBSettings = DBSettings()

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
