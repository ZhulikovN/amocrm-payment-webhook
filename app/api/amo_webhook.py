"""API endpoint для обработки webhook от amoCRM."""

import logging
from typing import Any
from urllib.parse import parse_qs, unquote_plus

from fastapi import APIRouter, HTTPException, Request

from app.services.webhook_processor import CatalogWebhookProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/amo", tags=["amoCRM Webhooks"])


@router.post("/webhook/handle")
async def handle_amo_webhook(request: Request) -> dict[str, Any]:
    """
    Обрабатывает webhook от amoCRM о добавлении/изменении элемента каталога 'Счета/покупки'.

    Возвращает:
        dict: Статус обработки webhook
    """
    try:
        # Парсим тело запроса
        raw_body = await request.body()
        text_body = raw_body.decode("utf-8", errors="ignore")

        logger.info("Получен webhook от amoCRM")

        decoded = unquote_plus(text_body)
        parsed_data = parse_qs(decoded)

        processor = CatalogWebhookProcessor()
        result = await processor.process_catalog_webhook(parsed_data)

        return result

    except ValueError as e:
        logger.error("Ошибка валидации webhook: %s", e)
        return {"status": "error", "error": str(e)}

    except Exception as e:
        logger.exception("Ошибка при обработке webhook от amoCRM: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error") from e
