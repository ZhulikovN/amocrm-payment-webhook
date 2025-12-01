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

    AMO_CLASS_YOUNGER_9: int = Field(
        ...,
        description="ID значения 'Младше 9 класса' в поле 'В каком классе учится'",
    )

    AMO_CLASS_9: int = Field(
        ...,
        description="ID значения '9 класс' в поле 'В каком классе учится'",
    )

    AMO_CLASS_10: int = Field(
        ...,
        description="ID значения '10 класс' в поле 'В каком классе учится'",
    )

    AMO_CLASS_11: int = Field(
        ...,
        description="ID значения '11 класс' в поле 'В каком классе учится'",
    )

    AMO_CLASS_UNIVERSITY: int = Field(
        ...,
        description="ID значения 'Университет' в поле 'В каком классе учится'",
    )

    AMO_CLASS_NOT_STUDENT: int = Field(
        ...,
        description="ID значения 'Не ученик' в поле 'В каком классе учится'",
    )

    AMO_CLASS_7: int = Field(
        ...,
        description="ID значения '7 класс' в поле 'В каком классе учится'",
    )

    AMO_CLASS_8: int = Field(
        ...,
        description="ID значения '8 класс' в поле 'В каком классе учится'",
    )

    AMO_CLASS_5_6: int = Field(
        ...,
        description="ID значения '5-6 класс' в поле 'В каком классе учится'",
    )

    AMO_COURSE_ALL_MYSELF: int = Field(
        ...,
        description="ID значения 'Все сам' в поле 'Какой курс куплен'",
    )

    AMO_COURSE_COMFORTIK: int = Field(
        ...,
        description="ID значения 'Комфортик' в поле 'Какой курс куплен'",
    )

    AMO_COURSE_NA_MAKSIMALKAH: int = Field(
        ...,
        description="ID значения 'На максималках' в поле 'Какой курс куплен'",
    )

    AMO_COURSE_POLUGODOVOY_OGE: int = Field(
        ...,
        description="ID значения 'Полугодовой ОГЭ' в поле 'Какой курс куплен'",
    )

    AMO_COURSE_NORMIS: int = Field(
        ...,
        description="ID значения 'Нормис' в поле 'Какой курс куплен'",
    )

    AMO_COURSE_IMBA: int = Field(
        ...,
        description="ID значения 'Имба' в поле 'Какой курс куплен'",
    )

    AMO_COURSE_SPETSKURS: int = Field(
        ...,
        description="ID значения 'Спецкурс' в поле 'Какой курс куплен'",
    )

    AMO_COURSE_NU_NORM: int = Field(
        ...,
        description="ID значения 'Ну норм' в поле 'Какой курс куплен'",
    )

    AMO_COURSE_SYN_MAMINOY_PODRUGE: int = Field(
        ...,
        description="ID значения 'Сын маминой подруги' в поле 'Какой курс куплен'",
    )

    AMO_COURSE_PROHODKA_NA_BYUDZHET: int = Field(
        ...,
        description="ID значения 'Проходка на бюджет' в поле 'Какой курс куплен'",
    )

    AMO_COURSE_SHIK_BLESK: int = Field(
        ...,
        description="ID значения 'Шик блеск' в поле 'Какой курс куплен'",
    )

    AMO_COURSE_STANDART: int = Field(
        ...,
        description="ID значения 'Стандарт' в поле 'Какой курс куплен'",
    )

    AMO_COURSE_SAMOSTOYATELNYY: int = Field(
        ...,
        description="ID значения 'Самостоятельный' в поле 'Какой курс куплен'",
    )

    AMO_COURSE_PLATINUM: int = Field(
        ...,
        description="ID значения 'Платинум' в поле 'Какой курс куплен'",
    )

    AMO_LEAD_FIELD_CLASS: int = Field(
        ...,
        description="ID поля 'В каком классе учится' в сделке (select)",
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
