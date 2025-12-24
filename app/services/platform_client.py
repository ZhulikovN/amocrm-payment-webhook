"""Клиент для отправки данных на платформу."""

import hashlib
import hmac
import json
import logging

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.models.platform import PlatformPayload
from app.settings import settings

logger = logging.getLogger(__name__)


class PlatformClient:
    """Клиент для отправки webhook на платформу."""

    def __init__(self) -> None:
        """Инициализация клиента платформы."""
        self.platform_url = settings.PLATFORM_URL
        self.secret_key = settings.API_SECRET_KEY

    async def send_payment(self, payload: PlatformPayload) -> dict[str, str]:
        """
        Отправить данные об оплате на платформу.

        Args:
            payload: Данные для отправки

        Returns:
            dict: Ответ от платформы {"status": "success", "order_id": "..."}

        Raises:
            httpx.HTTPError: При ошибке отправки
        """
        logger.info("Отправка данных на платформу: %s", self.platform_url)

        # Сериализуем payload в JSON
        body_dict = payload.model_dump(mode="json", exclude_none=False)
        body_str = json.dumps(body_dict, separators=(",", ":"), ensure_ascii=False)

        # Генерируем HMAC SHA256 подпись
        signature = self._generate_signature(body_str)

        headers = {
            "X-API-KEY": signature,
            "Content-Type": "application/json",
        }

        endpoint = f"{self.platform_url}/api/amo/payment/callback"

        logger.info("Sending POST %s", endpoint)
        logger.debug("Request body: %s", body_str)
        logger.debug("Signature: %s", signature)

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(settings.MAX_RETRY_ATTEMPTS),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError)),
        ):
            with attempt:
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.post(
                            endpoint,
                            headers=headers,
                            content=body_str,
                        )

                        if response.status_code == 429:
                            logger.warning("Platform rate limit exceeded, retrying...")
                            response.raise_for_status()

                        response.raise_for_status()

                        logger.info("Platform response: %s", response.status_code)
                        logger.debug("Response body: %s", response.text)

                        return response.json() if response.text else {"status": "success"}

                except httpx.HTTPError as e:
                    logger.error("Platform API error: %s", e)
                    if isinstance(e, httpx.HTTPStatusError):
                        resp = e.response
                        logger.error("Status code: %s", resp.status_code)
                        logger.error("Response text: %s", resp.text)

                    raise

        return {"status": "error"}

    def _generate_signature(self, body: str) -> str:
        """
        Генерировать HMAC SHA256 подпись для тела запроса.

        Args:
            body: Тело запроса в формате JSON string

        Returns:
            str: Hex-строка подписи
        """
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            body.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        logger.debug("Generated signature for body (length: %s): %s", len(body), signature)

        return signature

