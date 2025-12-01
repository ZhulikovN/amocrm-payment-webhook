import logging

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения для интеграции amoCRM → Платформа."""

    AMO_BASE_URL: str = Field(
        ...,
        description="Базовый URL amoCRM аккаунта",
    )

    AMO_LONG_LIVE_TOKEN: str = Field(
        ...,
        description="Долгосрочный токен для доступа к API amoCRM",
    )

    PLATFORM_URL: str = Field(
        ...,
        description="URL платформы для отправки webhook",
    )

    API_SECRET_KEY: str = Field(
        ...,
        description="Секретный ключ для формирования HMAC SHA256 подписи",
    )

    AMO_SUBJECT_OBSHCHESTVO: int = Field(
        ...,
        description="ID значения 'Обществознание' в поле 'Какой предмет выбрал'",
    )

    AMO_SUBJECT_ENGLISH: int = Field(
        ...,
        description="ID значения 'Английский язык' в поле 'Какой предмет выбрал'",
    )

    AMO_SUBJECT_HISTORY: int = Field(
        ...,
        description="ID значения 'История' в поле 'Какой предмет выбрал'",
    )

    AMO_SUBJECT_RUSSIAN: int = Field(
        ...,
        description="ID значения 'Русский' в поле 'Какой предмет выбрал'",
    )

    AMO_SUBJECT_PHYSICS: int = Field(
        ...,
        description="ID значения 'Физика' в поле 'Какой предмет выбрал'",
    )

    AMO_SUBJECT_CHEMISTRY: int = Field(
        ...,
        description="ID значения 'Химия' в поле 'Какой предмет выбрал'",
    )

    AMO_SUBJECT_LITERATURE: int = Field(
        ...,
        description="ID значения 'Литература' в поле 'Какой предмет выбрал'",
    )

    AMO_SUBJECT_MATH_PROF_MASHA: int = Field(
        ...,
        description="ID значения 'Профиль Маша' в поле 'Какой предмет выбрал'",
    )

    AMO_SUBJECT_MATH_BASE: int = Field(
        ...,
        description="ID значения 'Математика (база)' в поле 'Какой предмет выбрал'",
    )

    AMO_SUBJECT_BIOLOGY_ZHENYA: int = Field(
        ...,
        description="ID значения 'Биология (Женя)' в поле 'Какой предмет выбрал'",
    )

    AMO_SUBJECT_BIOLOGY_GELYA: int = Field(
        ...,
        description="ID значения 'Биология (Геля)' в поле 'Какой предмет выбрал'",
    )

    AMO_SUBJECT_INFORMATICS: int = Field(
        ...,
        description="ID значения 'Информатика' в поле 'Какой предмет выбрал'",
    )

    AMO_SUBJECT_MATH_PROF_SASHA: int = Field(
        ...,
        description="ID значения 'Профиль Саша' в поле 'Какой предмет выбрал'",
    )

    AMO_SUBJECT_MATH_7_8: int = Field(
        ...,
        description="ID значения 'Математика 7-8 класс' в поле 'Какой предмет выбрал'",
    )

    AMO_SUBJECT_MATH_OGE: int = Field(
        ...,
        description="ID значения 'Математика ОГЭ' в поле 'Какой предмет выбрал'",
    )

    AMO_LEAD_FIELD_SUBJECTS: int = Field(
        ...,
        description="ID поля 'Какой предмет выбрал' в сделке (multiselect)",
    )

    AMO_LEAD_FIELD_DIRECTION: int = Field(
        ...,
        description="ID поля 'Направление курса' в сделке",
    )

    AMO_LEAD_FIELD_PURCHASED_COURSE: int = Field(
        ...,
        description="ID поля 'Какой курс куплен' в сделке",
    )

    CREATE_LEAD_IF_NOT_FOUND: bool = Field(
        default=False,
        description="Создавать ли новую сделку, если не найдена существующая",
    )

    MAX_RETRY_ATTEMPTS: int = Field(
        default=3,
        description="Максимальное количество попыток повторной отправки при ошибке",
    )

    RETRY_DELAY_SECONDS: int = Field(
        default=300,
        description="Задержка между попытками повторной отправки (в секундах)",
    )

    LOG_LEVEL: str = Field(
        default="INFO",
        description="Уровень логирования (DEBUG, INFO, WARNING, ERROR)",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def log_level_value(self) -> int:
        """Возвращает числовой уровень логирования для logging.basicConfig."""
        return getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)


settings = Settings()  # type: ignore[call-arg]
