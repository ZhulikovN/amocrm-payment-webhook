"""Маппер для преобразования данных из webhook каталога + amoCRM в payload для платформы."""

import logging
from typing import Any

from app.config.subject_mapping import (
    get_tariff_suffix,
    map_class_to_number,
    map_course_name_text,
    map_subject_to_designation,
)
from app.models.platform import Course, PlatformPayload
from app.settings import settings

logger = logging.getLogger(__name__)


class PaymentPayloadMapper:
    """Маппер для создания payload платформы из данных webhook + amoCRM."""

    def map_to_platform_payload(
        self,
        items: list[dict[str, str | int]],
        amount: int,
        client_data: dict[str, Any],
    ) -> PlatformPayload:
        """
        Создать payload для отправки на платформу.

        Args:
            items: Позиции счета из webhook [{description, unit_price, quantity}, ...]
            amount: Общая сумма из webhook (BILL_PRICE)
            client_data: Данные клиента из amoCRM (из extract_lead_data)

        Returns:
            PlatformPayload: Готовый payload для отправки

        Raises:
            ValueError: Если отсутствуют обязательные данные
        """
        logger.info("Маппинг данных в payload платформы")

        class_enum_id = client_data.get("class_enum_id")
        if not class_enum_id:
            raise ValueError("Отсутствует поле 'class_enum_id' в данных клиента")

        subjects_enum_ids = client_data.get("subjects_enum_ids", [])
        if not subjects_enum_ids:
            raise ValueError("Отсутствует поле 'subjects_enum_ids' в данных клиента")

        contact_name = client_data.get("contact_name", "")
        contact_phone = client_data.get("contact_phone")
        contact_email = client_data.get("contact_email")

        if not contact_phone:
            raise ValueError("Отсутствует телефон контакта")

        if not contact_email:
            raise ValueError("Отсутствует email контакта")

        class_number = map_class_to_number(class_enum_id)
        logger.info("Mapped class: enum_id=%s → number=%s", class_enum_id, class_number)

        # Получаем тариф (первый из списка или None)
        purchased_course_enum_ids = client_data.get("purchased_course_enum_ids", [])
        tariff_id = purchased_course_enum_ids[0] if purchased_course_enum_ids else None
        
        first_name, last_name = self._parse_name(contact_name)

        # Строим список курсов из позиций счета + предметов из amoCRM
        courses = self._build_courses(items, subjects_enum_ids, tariff_id)

        payload = PlatformPayload(
            courses=courses,
            first_name=first_name,
            last_name=last_name,
            email=contact_email,
            phone=contact_phone,
            amount=amount,
            **{"class": class_number},
        )

        logger.info(
            "Payload создан: %s курсов, сумма=%s, клиент=%s %s (%s)",
            len(courses),
            amount,
            first_name,
            last_name,
            contact_email,
        )

        return payload

    def _build_courses(
        self,
        items: list[dict[str, str | int]],
        subjects_enum_ids: list[int],
        tariff_id: int | None = None,
    ) -> list[Course]:
        """
        Создать список курсов из позиций счета + предметов из amoCRM.

        Args:
            items: Позиции счета [{description, unit_price, quantity}, ...]
            subjects_enum_ids: Список enum_id предметов из amoCRM
            tariff_id: ID тарифа из поля 'Какой курс куплен' (для добавления к названию)

        Returns:
            list[Course]: Список курсов для платформы

        Raises:
            ValueError: Если количество позиций и предметов не совпадает
        """
        if len(items) != len(subjects_enum_ids):
            raise ValueError(
                f"Количество позиций счета ({len(items)}) не совпадает "
                f"с количеством предметов ({len(subjects_enum_ids)})"
            )

        courses = []

        for idx, (item, subject_enum_id) in enumerate(zip(items, subjects_enum_ids)):
            description = str(item.get("description", ""))
            unit_price = int(item.get("unit_price", 0))
            quantity = int(item.get("quantity", 1))

            if not description:
                logger.warning("Пропускаем позицию %s: пустое название", idx)
                continue

            try:
                mapped_name = map_course_name_text(description)
                logger.info("Название курса замаплено: '%s' → '%s'", description, mapped_name)
            except ValueError as e:
                logger.error("Ошибка маппинга названия курса: %s", e)
                raise

            # Добавляем тариф к названию ТОЛЬКО если курс поддерживает этот тариф
            # Весенний курс 2к26: Standart (EN), PRO (EN), Самостоятельный (RU)
            # Марафон 2к26: Базовый (RU), Стандарт (RU), ПРО (RU)
            # Годовой 2к27: ТОЛЬКО Стандарт (RU)
            final_name = mapped_name
            
            if tariff_id:
                tariff_suffix = None
                
                # Весенний курс 2к26: тарифы на английском/русском
                if "Весенний курс 2к26" in mapped_name:
                    if tariff_id == settings.AMO_COURSE_STANDART:
                        tariff_suffix = "Standart"  # Английский
                    elif tariff_id == settings.AMO_COURSE_PRO:
                        tariff_suffix = "PRO"  # Английский
                    elif tariff_id == settings.AMO_COURSE_SAMOSTOYATELNYY:
                        tariff_suffix = "Самостоятельный"  # Русский
                    else:
                        logger.warning("Тариф %s не поддерживается для Весенний курс 2к26, пропускаем", tariff_id)
                
                # Марафон 2к26: Базовый, Стандарт, ПРО (русский)
                elif "Марафон 2к26" in mapped_name:
                    if tariff_id == settings.AMO_COURSE_STANDART:
                        tariff_suffix = "Стандарт"  # Русский
                    elif tariff_id == settings.AMO_COURSE_PRO:
                        tariff_suffix = "ПРО"  # Русский
                    elif tariff_id == settings.AMO_COURSE_BAZOVYY:
                        tariff_suffix = "Базовый"  # Русский
                    else:
                        logger.warning("Тариф %s не поддерживается для Марафон 2к26, пропускаем", tariff_id)
                
                # Годовой 2к27: ТОЛЬКО Стандарт (русский)
                elif "Годовой 2к27" in mapped_name:
                    if tariff_id == settings.AMO_COURSE_STANDART:
                        tariff_suffix = "Стандарт"  # Русский
                    else:
                        logger.warning("Тариф %s не поддерживается для Годовой 2к27 (только Стандарт), пропускаем", tariff_id)
                
                if tariff_suffix:
                    final_name = f"{mapped_name} {tariff_suffix}"
                    logger.info("Добавлен тариф к названию: '%s' → '%s'", mapped_name, final_name)

            subject_designation = map_subject_to_designation(subject_enum_id)

            course = Course(
                name=final_name,
                subject_designation=subject_designation,
                cost=unit_price,
                months=quantity,
            )

            courses.append(course)
            logger.info(
                "Курс [%s]: %s → %s (цена: %s, месяцы: %s)",
                idx,
                description,
                subject_designation,
                unit_price,
                quantity,
            )

        if not courses:
            raise ValueError("Не удалось создать ни одного курса из позиций счета")

        return courses

    def _parse_name(self, full_name: str) -> tuple[str, str | None]:
        """
        Разделить полное имя на имя и фамилию.

        Args:
            full_name: Полное имя из amoCRM

        Returns:
            tuple: (first_name, last_name)
        """
        if not full_name:
            logger.warning("Пустое имя клиента, используем 'Клиент'")
            return "Клиент", None

        parts = full_name.strip().split(maxsplit=1)

        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else None

        logger.debug("Parsed name: '%s' → first_name='%s', last_name='%s'", full_name, first_name, last_name)

        return first_name, last_name
