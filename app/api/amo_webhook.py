"""Обработчик webhook от amoCRM для событий каталога 'Счета/покупки'."""

import logging
import re
from urllib.parse import parse_qs, unquote_plus

from fastapi import APIRouter, HTTPException, Request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/amo", tags=["amoCRM Webhooks"])


@router.post("/webhook/handle")
async def handle_amo_webhook(request: Request) -> dict[str, str]:
    """
    Обрабатывает webhook от amoCRM о добавлении/изменении элемента каталога 'Счета/покупки'.

    amoCRM отправляет данные в формате application/x-www-form-urlencoded.
    Структура webhook:
    - account[subdomain] - поддомен аккаунта
    - account[id] - ID аккаунта
    - catalogs[add/update][0][id] - ID элемента каталога
    - catalogs[add/update][0][catalog_id] - ID каталога (6640 для Счета/покупки)
    - catalogs[add/update][0][custom_fields][N][code] - код поля
    - catalogs[add/update][0][custom_fields][N][values][0][value] - значение поля

    Ключевые поля:
    - LINK_TO_LEAD - ссылка на сделку
    - BILL_STATUS - статус счета ("Оплачен" / "Создан")
    - ITEMS - позиции счета (description, unit_price, quantity)
    - BILL_PRICE - общая стоимость

    Возвращает:
        dict: Статус обработки webhook
    """
    try:
        raw_body = await request.body()
        text_body = raw_body.decode("utf-8", errors="ignore")

        logger.info("Получен webhook от amoCRM")

        decoded = unquote_plus(text_body)
        parsed_data = parse_qs(decoded)

        # logger.info("Parsed webhook data: %s", parsed_data)

        # Проверяем тип события (catalogs[add] или catalogs[update])
        event_type = _detect_catalog_event_type(parsed_data)
        if not event_type:
            logger.warning("Webhook не является событием каталога")
            return {"status": "ignored", "reason": "not_catalog_event"}

        logger.info("Обнаружено событие каталога: %s", event_type)

        # Проверяем статус оплаты
        if not _is_paid(parsed_data, event_type):
            logger.info("Счет не оплачен, пропускаем")
            return {"status": "ignored", "reason": "not_paid"}

        # Извлекаем данные
        catalog_element_id = _extract_catalog_element_id(parsed_data, event_type)
        lead_id = _extract_lead_id(parsed_data, event_type)
        items = _extract_items(parsed_data, event_type)
        amount = _extract_amount(parsed_data, event_type)

        if not lead_id:
            logger.warning("Не удалось извлечь lead_id из webhook")
            return {"status": "ignored", "reason": "missing_lead_id"}

        if not items:
            logger.warning("Не удалось извлечь позиции счета из webhook")
            return {"status": "ignored", "reason": "missing_items"}

        logger.info(
            "✓ Обнаружена оплата: catalog_element_id=%s, lead_id=%s, items_count=%s, amount=%s",
            catalog_element_id,
            lead_id,
            len(items),
            amount,
        )

        # TODO: Вызвать обработку payment processor
        # await process_payment(lead_id=lead_id, items=items, amount=amount)

        return {
            "status": "success",
            "catalog_element_id": str(catalog_element_id),
            "lead_id": str(lead_id),
            "items_count": str(len(items)),
            "amount": str(amount),
        }

    except Exception as e:
        logger.exception("Ошибка при обработке webhook от amoCRM: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error") from e


def _detect_catalog_event_type(parsed_data: dict[str, list[str]]) -> str | None:
    """
    Определяет тип события каталога (add или update).

    Args:
        parsed_data: Распарсенные данные webhook

    Returns:
        str | None: "add" или "update" или None если не событие каталога
    """
    if any(key.startswith("catalogs[add][0]") for key in parsed_data.keys()):
        return "add"
    if any(key.startswith("catalogs[update][0]") for key in parsed_data.keys()):
        return "update"
    return None


def _is_paid(parsed_data: dict[str, list[str]], event_type: str) -> bool:
    """
    Проверяет, является ли статус счета "Оплачен".

    Args:
        parsed_data: Распарсенные данные webhook
        event_type: Тип события ("add" или "update")

    Returns:
        bool: True если статус = "Оплачен" (enum 1371080)
    """
    # Ищем поле BILL_STATUS
    # Формат ключа: catalogs[update][0][custom_fields][1][code]
    for key, values in parsed_data.items():
        if f"catalogs[{event_type}][0][custom_fields]" in key and "[code]" in key:
            if values and values[0] == "BILL_STATUS":
                # Извлекаем индекс поля из ключа
                # catalogs[update][0][custom_fields][1][code] -> нужен индекс [1]
                parts = key.split("[")
                field_index = f"[{parts[4]}"  # [1]
                
                enum_key = f"catalogs[{event_type}][0][custom_fields]{field_index}[values][0][enum]"
                value_key = f"catalogs[{event_type}][0][custom_fields]{field_index}[values][0][value]"
                
                enum_value = parsed_data.get(enum_key, [])
                status_value = parsed_data.get(value_key, [])
                
                status_text = status_value[0] if status_value else "N/A"
                enum_text = enum_value[0] if enum_value else "N/A"
                
                if enum_value and enum_value[0] == "1371080":  # Оплачен
                    logger.info("✓ Статус счета: %s (enum: %s)", status_text, enum_text)
                    return True
                
                logger.info("✗ Статус счета: %s (enum: %s) - игнорируем", status_text, enum_text)
                return False
    
    logger.warning("Поле BILL_STATUS не найдено в webhook")
    return False


def _extract_catalog_element_id(parsed_data: dict[str, list[str]], event_type: str) -> int | None:
    """
    Извлекает ID элемента каталога.

    Args:
        parsed_data: Распарсенные данные webhook
        event_type: Тип события ("add" или "update")

    Returns:
        int | None: ID элемента каталога или None
    """
    key = f"catalogs[{event_type}][0][id]"
    element_id_list = parsed_data.get(key, [])
    if not element_id_list:
        return None

    try:
        return int(element_id_list[0])
    except (ValueError, IndexError):
        return None


def _extract_lead_id(parsed_data: dict[str, list[str]], event_type: str) -> int | None:
    """
    Извлекает ID сделки из поля LINK_TO_LEAD.

    Args:
        parsed_data: Распарсенные данные webhook
        event_type: Тип события ("add" или "update")

    Returns:
        int | None: ID сделки или None
    """
    # Ищем поле LINK_TO_LEAD
    # Формат: catalogs[update][0][custom_fields][0][code]: ['LINK_TO_LEAD']
    for key, values in parsed_data.items():
        if f"catalogs[{event_type}][0][custom_fields]" in key and "[code]" in key:
            if values and values[0] == "LINK_TO_LEAD":
                # Извлекаем индекс поля
                parts = key.split("[")
                field_index = f"[{parts[4]}"  # [0]
                
                value_key = f"catalogs[{event_type}][0][custom_fields]{field_index}[values][0][value]"
                link = parsed_data.get(value_key, [])
                
                if link:
                    # Парсим URL: https://egeland.amocrm.ru/leads/detail/39553937 → 39553937
                    match = re.search(r"/leads/detail/(\d+)", link[0])
                    if match:
                        lead_id = int(match.group(1))
                        logger.info("Извлечен lead_id: %s из ссылки: %s", lead_id, link[0])
                        return lead_id
    
    logger.warning("Поле LINK_TO_LEAD не найдено в webhook")
    return None


def _extract_items(parsed_data: dict[str, list[str]], event_type: str) -> list[dict[str, str | int]]:
    """
    Извлекает позиции счета (ITEMS) из webhook.

    Args:
        parsed_data: Распарсенные данные webhook
        event_type: Тип события ("add" или "update")

    Returns:
        list: Список позиций [{description, unit_price, quantity}, ...]
    """
    items = []

    # Находим индекс поля ITEMS
    # Формат: catalogs[update][0][custom_fields][5][code]: ['ITEMS']
    items_field_index = None
    for key, values in parsed_data.items():
        if f"catalogs[{event_type}][0][custom_fields]" in key and "[code]" in key:
            if values and values[0] == "ITEMS":
                parts = key.split("[")
                items_field_index = f"[{parts[4]}"  # [5]
                break

    if not items_field_index:
        logger.warning("Поле ITEMS не найдено в webhook")
        return items

    # Собираем все позиции
    # Формат: catalogs[add][0][custom_fields][5][values][0][value][description]
    item_index = 0
    while True:
        base_key = f"catalogs[{event_type}][0][custom_fields]{items_field_index}[values][{item_index}][value]"

        description_key = f"{base_key}[description]"
        unit_price_key = f"{base_key}[unit_price]"
        quantity_key = f"{base_key}[quantity]"

        description = parsed_data.get(description_key, [])
        unit_price = parsed_data.get(unit_price_key, [])
        quantity = parsed_data.get(quantity_key, [])

        if not description:  # Больше нет позиций
            break

        try:
            item = {
                "description": description[0] if description else "",
                "unit_price": int(unit_price[0]) if unit_price else 0,
                "quantity": int(quantity[0]) if quantity else 0,
            }
            items.append(item)
            logger.debug("Позиция %s: %s (цена: %s, кол-во: %s)", 
                        item_index, item["description"], item["unit_price"], item["quantity"])
        except (ValueError, IndexError) as e:
            logger.warning("Ошибка при парсинге позиции %s: %s", item_index, e)

        item_index += 1

    logger.info("Извлечено позиций счета: %s", len(items))
    for idx, item in enumerate(items):
        logger.info("  [%s] %s - %s руб x %s мес", idx, item["description"], item["unit_price"], item["quantity"])
    
    return items


def _extract_amount(parsed_data: dict[str, list[str]], event_type: str) -> int:
    """
    Извлекает общую стоимость (BILL_PRICE) из webhook.

    Args:
        parsed_data: Распарсенные данные webhook
        event_type: Тип события ("add" или "update")

    Returns:
        int: Общая стоимость или 0
    """
    for key, values in parsed_data.items():
        if f"catalogs[{event_type}][0][custom_fields]" in key and "[code]" in key:
            if values and values[0] == "BILL_PRICE":
                parts = key.split("[")
                field_index = f"[{parts[4]}"  # [6] или [7]
                
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
