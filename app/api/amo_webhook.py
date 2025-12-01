"""Обработчик webhook от amoCRM для событий добавления примечаний."""

import logging
from urllib.parse import parse_qs, unquote_plus

from fastapi import APIRouter, HTTPException, Request

from app.services.note_parser import is_payment_note

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/amo", tags=["amoCRM Webhooks"])


@router.post("/webhook")
async def handle_amo_webhook(request: Request) -> dict[str, str]:
    """
    Обрабатывает webhook от amoCRM о добавлении примечания в сделку.

    amoCRM отправляет данные в формате application/x-www-form-urlencoded.
    Структура webhook:
    - account[subdomain] - поддомен аккаунта
    - account[id] - ID аккаунта
    - leads[note][0][note][text] - текст примечания
    - leads[note][0][note][element_id] - ID сделки
    - leads[note][0][note][id] - ID примечания
    - leads[note][0][note][metadata] - метаданные (JSON строка)

    Возвращает:
        dict: Статус обработки webhook
    """
    try:
        raw_body = await request.body()
        text_body = raw_body.decode("utf-8", errors="ignore")

        logger.info("Получен webhook от amoCRM")
        logger.debug("Raw body: %s", text_body)

        decoded = unquote_plus(text_body)
        parsed_data = parse_qs(decoded)

        logger.debug("Parsed data: %s", parsed_data)

        if not _is_note_event(parsed_data):
            logger.warning("Webhook не является событием добавления примечания")
            return {"status": "ignored", "reason": "not_a_note_event"}

        note_text = _extract_note_text(parsed_data)
        lead_id = _extract_lead_id(parsed_data)
        note_id = _extract_note_id(parsed_data)

        if not note_text or not lead_id:
            logger.warning("Не удалось извлечь данные из webhook: note_text=%s, lead_id=%s", note_text, lead_id)
            return {"status": "ignored", "reason": "missing_data"}

        logger.info("Обработка примечания: lead_id=%s, note_id=%s, text=%s", lead_id, note_id, note_text)

        if not is_payment_note(note_text):
            logger.info("Примечание не является платежным, пропускаем: %s", note_text)
            return {"status": "ignored", "reason": "not_payment_note"}

        logger.info("✓ Обнаружено примечание об оплате для сделки %s", lead_id)

        # TODO: Вызвать обработку payment processor

        return {"status": "success", "lead_id": str(lead_id), "note_id": str(note_id)}

    except Exception as e:
        logger.exception("Ошибка при обработке webhook от amoCRM: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error") from e


def _is_note_event(parsed_data: dict[str, list[str]]) -> bool:
    """
    Проверяет, является ли webhook событием добавления примечания.

    Args:
        parsed_data: Распарсенные данные webhook

    Returns:
        bool: True если это событие добавления примечания
    """
    return "leads[note][0][note][text]" in parsed_data


def _extract_note_text(parsed_data: dict[str, list[str]]) -> str | None:
    """
    Извлекает текст примечания из webhook данных.

    Args:
        parsed_data: Распарсенные данные webhook

    Returns:
        str | None: Текст примечания или None
    """
    note_text_list = parsed_data.get("leads[note][0][note][text]", [])
    return note_text_list[0] if note_text_list else None


def _extract_lead_id(parsed_data: dict[str, list[str]]) -> int | None:
    """
    Извлекает ID сделки из webhook данных.

    Args:
        parsed_data: Распарсенные данные webhook

    Returns:
        int | None: ID сделки или None
    """
    lead_id_list = parsed_data.get("leads[note][0][note][element_id]", [])
    if not lead_id_list:
        return None

    try:
        return int(lead_id_list[0])
    except (ValueError, IndexError):
        return None


def _extract_note_id(parsed_data: dict[str, list[str]]) -> int | None:
    """
    Извлекает ID примечания из webhook данных.

    Args:
        parsed_data: Распарсенные данные webhook

    Returns:
        int | None: ID примечания или None
    """
    note_id_list = parsed_data.get("leads[note][0][note][id]", [])
    if not note_id_list:
        return None

    try:
        return int(note_id_list[0])
    except (ValueError, IndexError):
        return None
