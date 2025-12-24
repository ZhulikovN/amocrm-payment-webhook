"""Процессор для обработки webhook от amoCRM каталога 'Счета/покупки'."""

import logging
import re
from typing import Any

from app.services.amocrm_client import AmoCRMClient
from app.services.mapper import PaymentPayloadMapper
from app.services.platform_client import PlatformClient

logger = logging.getLogger(__name__)


class CatalogWebhookProcessor:
    """Процессор для обработки webhook каталога Счета/покупки."""

    def __init__(self) -> None:
        """Инициализация процессора."""
        self.amo_client = AmoCRMClient()
        self.mapper = PaymentPayloadMapper()
        self.platform_client = PlatformClient()

    async def process_catalog_webhook(self, parsed_data: dict[str, list[str]]) -> dict[str, Any]:
        """
        Обработать webhook от amoCRM.

        Args:
            parsed_data: Распарсенные данные webhook (parse_qs result)

        Returns:
            dict: Результат обработки

        Raises:
            ValueError: При ошибках валидации или обработки
        """
        # Проверяем тип события
        event_type = self._detect_event_type(parsed_data)
        if not event_type:
            logger.warning("Webhook не является событием каталога")
            return {"status": "ignored", "reason": "not_catalog_event"}

        logger.info("Обнаружено событие каталога: %s", event_type)

        # Проверяем статус оплаты
        if not self._is_paid(parsed_data, event_type):
            logger.info("Счет не оплачен, пропускаем")
            return {"status": "ignored", "reason": "not_paid"}

        # Извлекаем данные
        catalog_element_id = self._extract_catalog_element_id(parsed_data, event_type)
        lead_id = self._extract_lead_id(parsed_data, event_type)
        items = self._extract_items(parsed_data, event_type)
        amount = self._extract_amount(parsed_data, event_type)

        if not lead_id:
            raise ValueError("Не удалось извлечь lead_id из webhook")

        if not items:
            raise ValueError("Не удалось извлечь позиции счета из webhook")

        logger.info(
            "Обнаружена оплата: catalog_element_id=%s, lead_id=%s, items_count=%s, amount=%s",
            catalog_element_id,
            lead_id,
            len(items),
            amount,
        )

        # Обрабатываем платеж
        platform_response = await self._process_payment(lead_id=lead_id, items=items, amount=amount)

        return {
            "status": "success",
            "catalog_element_id": str(catalog_element_id),
            "lead_id": str(lead_id),
            "platform_response": platform_response,
        }

    async def _process_payment(
        self,
        lead_id: int,
        items: list[dict[str, str | int]],
        amount: int,
    ) -> dict[str, str]:
        """
        Обработать платеж: загрузить данные из amoCRM, смаппить и отправить на платформу.

        Args:
            lead_id: ID сделки из amoCRM
            items: Позиции счета из webhook
            amount: Общая сумма

        Returns:
            dict: Ответ от платформы

        Raises:
            Exception: При ошибке обработки
        """
        logger.info("Начало обработки платежа для lead_id=%s", lead_id)

        # 1. Загружаем данные клиента из amoCRM
        lead_and_contact = await self.amo_client.get_lead_with_contact(lead_id)
        client_data = self.amo_client.extract_lead_data(lead_and_contact["lead"], lead_and_contact["contact"])

        logger.info("Данные клиента загружены: %s", client_data.get("contact_email"))

        # 2. Маппим данные в payload платформы
        payload = self.mapper.map_to_platform_payload(
            items=items,
            amount=amount,
            client_data=client_data,
        )

        logger.info("Payload создан для отправки на платформу")

        # 3. Отправляем на платформу
        response = await self.platform_client.send_payment(payload)

        logger.info("✓ Платеж успешно отправлен на платформу: %s", response)

        return response

    def _detect_event_type(self, parsed_data: dict[str, list[str]]) -> str | None:
        """
        Определить тип события каталога.

        Args:
            parsed_data: Распарсенные данные webhook

        Returns:
            str | None: "add" или "update" или None
        """
        if any(key.startswith("catalogs[add][0]") for key in parsed_data.keys()):
            return "add"
        if any(key.startswith("catalogs[update][0]") for key in parsed_data.keys()):
            return "update"
        return None

    def _is_paid(self, parsed_data: dict[str, list[str]], event_type: str) -> bool:
        """
        Проверить статус оплаты.

        Args:
            parsed_data: Распарсенные данные webhook
            event_type: Тип события ("add" или "update")

        Returns:
            bool: True если статус = "Оплачен" (enum 1371080)
        """
        for key, values in parsed_data.items():
            if f"catalogs[{event_type}][0][custom_fields]" in key and "[code]" in key:
                if values and values[0] == "BILL_STATUS":
                    parts = key.split("[")
                    field_index = f"[{parts[4]}"

                    enum_key = f"catalogs[{event_type}][0][custom_fields]{field_index}[values][0][enum]"
                    value_key = f"catalogs[{event_type}][0][custom_fields]{field_index}[values][0][value]"

                    enum_value = parsed_data.get(enum_key, [])
                    status_value = parsed_data.get(value_key, [])

                    status_text = status_value[0] if status_value else "N/A"
                    enum_text = enum_value[0] if enum_value else "N/A"

                    if enum_value and enum_value[0] == "1371080":
                        logger.info("✓ Статус счета: %s (enum: %s)", status_text, enum_text)
                        return True

                    logger.info("✗ Статус счета: %s (enum: %s) - игнорируем", status_text, enum_text)
                    return False

        logger.warning("Поле BILL_STATUS не найдено в webhook")
        return False

    def _extract_catalog_element_id(self, parsed_data: dict[str, list[str]], event_type: str) -> int | None:
        """Извлечь ID элемента каталога."""
        key = f"catalogs[{event_type}][0][id]"
        element_id_list = parsed_data.get(key, [])
        if not element_id_list:
            return None

        try:
            return int(element_id_list[0])
        except (ValueError, IndexError):
            return None

    def _extract_lead_id(self, parsed_data: dict[str, list[str]], event_type: str) -> int | None:
        """Извлечь ID сделки из поля LINK_TO_LEAD."""
        for key, values in parsed_data.items():
            if f"catalogs[{event_type}][0][custom_fields]" in key and "[code]" in key:
                if values and values[0] == "LINK_TO_LEAD":
                    parts = key.split("[")
                    field_index = f"[{parts[4]}"

                    value_key = f"catalogs[{event_type}][0][custom_fields]{field_index}[values][0][value]"
                    link = parsed_data.get(value_key, [])

                    if link:
                        match = re.search(r"/leads/detail/(\d+)", link[0])
                        if match:
                            lead_id = int(match.group(1))
                            logger.info("Извлечен lead_id: %s из ссылки: %s", lead_id, link[0])
                            return lead_id

        logger.warning("Поле LINK_TO_LEAD не найдено в webhook")
        return None

    def _extract_items(self, parsed_data: dict[str, list[str]], event_type: str) -> list[dict[str, str | int]]:
        """Извлечь позиции счета (ITEMS) из webhook."""
        items = []

        # Находим индекс поля ITEMS
        items_field_index = None
        for key, values in parsed_data.items():
            if f"catalogs[{event_type}][0][custom_fields]" in key and "[code]" in key:
                if values and values[0] == "ITEMS":
                    parts = key.split("[")
                    items_field_index = f"[{parts[4]}"
                    break

        if not items_field_index:
            logger.warning("Поле ITEMS не найдено в webhook")
            return items

        # Собираем все позиции
        item_index = 0
        while True:
            base_key = f"catalogs[{event_type}][0][custom_fields]{items_field_index}[values][{item_index}][value]"

            description_key = f"{base_key}[description]"
            unit_price_key = f"{base_key}[unit_price]"
            quantity_key = f"{base_key}[quantity]"

            description = parsed_data.get(description_key, [])
            unit_price = parsed_data.get(unit_price_key, [])
            quantity = parsed_data.get(quantity_key, [])

            if not description:
                break

            try:
                item = {
                    "description": description[0] if description else "",
                    "unit_price": int(unit_price[0]) if unit_price else 0,
                    "quantity": int(quantity[0]) if quantity else 0,
                }
                items.append(item)
                logger.debug(
                    "Позиция %s: %s (цена: %s, кол-во: %s)",
                    item_index,
                    item["description"],
                    item["unit_price"],
                    item["quantity"],
                )
            except (ValueError, IndexError) as e:
                logger.warning("Ошибка при парсинге позиции %s: %s", item_index, e)

            item_index += 1

        logger.info("Извлечено позиций счета: %s", len(items))
        for idx, item in enumerate(items):
            logger.info("  [%s] %s - %s руб x %s мес", idx, item["description"], item["unit_price"], item["quantity"])

        return items

    def _extract_amount(self, parsed_data: dict[str, list[str]], event_type: str) -> int:
        """Извлечь общую стоимость (BILL_PRICE) из webhook."""
        for key, values in parsed_data.items():
            if f"catalogs[{event_type}][0][custom_fields]" in key and "[code]" in key:
                if values and values[0] == "BILL_PRICE":
                    parts = key.split("[")
                    field_index = f"[{parts[4]}"

                    value_key = f"catalogs[{event_type}][0][custom_fields]{field_index}[values][0][value]"
                    amount_str = parsed_data.get(value_key, [])

                    if amount_str:
                        try:
                            amount = int(amount_str[0])
                            logger.info("Извлечена общая сумма: %s руб", amount)
                            return amount
                        except (ValueError, IndexError) as e:
                            logger.warning("Ошибка при парсинге суммы: %s", e)

        logger.warning("Поле BILL_PRICE не найдено в webhook")
        return 0

