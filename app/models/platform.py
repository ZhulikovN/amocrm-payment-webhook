"""Модели данных для отправки на платформу."""

from pydantic import BaseModel, Field


class Course(BaseModel):
    """Модель курса для отправки на платформу."""

    name: str = Field(..., description="Название курса")
    subject_designation: str = Field(..., description="Обозначение предмета")
    cost: int = Field(..., description="Стоимость курса")
    months: int = Field(..., description="Количество месяцев")


class PlatformPayload(BaseModel):
    """Payload для отправки на платформу при оплате."""

    courses: list[Course] = Field(..., description="Список курсов в заказе")
    first_name: str = Field(..., description="Имя клиента")
    last_name: str | None = Field(None, description="Фамилия клиента")
    email: str = Field(..., description="Email клиента")
    phone: str = Field(..., description="Телефон клиента")
    class_number: int = Field(..., alias="class", description="Класс ученика (1-11)")
    amount: int = Field(..., description="Общая сумма заказа")

    class Config:
        """Настройки модели."""

        populate_by_name = True
