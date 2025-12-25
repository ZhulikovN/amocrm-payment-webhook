"""Клиент для работы с API amoCRM."""

import logging
from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.settings import settings

logger = logging.getLogger(__name__)


class AmoCRMClient:
    """Клиент для взаимодействия с API amoCRM."""

    def __init__(self) -> None:
        """Инициализация клиента amoCRM."""
        self.base_url = settings.AMO_BASE_URL
        self.access_token = settings.AMO_LONG_LIVE_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def _make_request(self, method: str, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Выполнить HTTP запрос к API amoCRM с retry механизмом.

        Args:
            method: HTTP метод (GET, POST, PATCH)
            endpoint: Endpoint API (например, /api/v4/leads/123)
            params: Параметры запроса (для GET)

        Returns:
            Ответ от API в виде dict

        Raises:
            httpx.HTTPError: При ошибке API
        """
        url = f"{self.base_url}{endpoint}"

        logger.info("AmoCRM API request: %s %s", method, url)
        if params:
            logger.debug("Request params: %s", params)

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(settings.MAX_RETRY_ATTEMPTS),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError)),
        ):
            with attempt:
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        if method == "GET":
                            response = await client.get(url, headers=self.headers, params=params)
                        else:
                            raise ValueError(f"Unsupported HTTP method: {method}")

                        if response.status_code == 429:
                            logger.warning("AmoCRM rate limit exceeded, retrying...")
                            response.raise_for_status()

                        response.raise_for_status()

                        logger.info("AmoCRM API response: %s", response.status_code)

                        return response.json() if response.text else {}

                except httpx.HTTPError as e:
                    logger.error("AmoCRM API error: %s", e)
                    if isinstance(e, httpx.HTTPStatusError):
                        resp = e.response
                        logger.error("Status code: %s", resp.status_code)
                        logger.error("Response text: %s", resp.text)

                    raise

        return {}

    async def get_lead_with_contact(self, lead_id: int) -> dict[str, Any]:
        """
        Получить полные данные сделки вместе с контактом.

        Args:
            lead_id: ID сделки

        Returns:
            dict: Данные сделки и контакта
            {
                "lead": {...},
                "contact": {...}
            }

        Raises:
            ValueError: Если сделка или контакт не найдены
        """
        logger.info("Fetching lead %s with contact data", lead_id)

        lead_data = await self._make_request("GET", f"/api/v4/leads/{lead_id}", params={"with": "contacts"})

        if not lead_data:
            raise ValueError(f"Lead {lead_id} not found")

        embedded_contacts = lead_data.get("_embedded", {}).get("contacts", [])

        if not embedded_contacts:
            raise ValueError(f"No contacts found for lead {lead_id}")

        contact_id = embedded_contacts[0]["id"]
        logger.info("Found contact %s for lead %s", contact_id, lead_id)

        contact_data = await self._make_request("GET", f"/api/v4/contacts/{contact_id}")

        if not contact_data:
            raise ValueError(f"Contact {contact_id} not found")

        return {"lead": lead_data, "contact": contact_data}

    def _parse_custom_fields(self, custom_fields_values: list[dict[str, Any]]) -> dict[int, Any]:
        """
        Преобразовать custom_fields_values в словарь {field_id: value}.

        Args:
            custom_fields_values: Список кастомных полей из amoCRM

        Returns:
            dict: Словарь {field_id: значение}
        """
        result: dict[int, Any] = {}

        for field in custom_fields_values:
            field_id = field.get("field_id")
            values = field.get("values", [])

            if not field_id or not values:
                continue

            if len(values) == 1:
                value_data = values[0]
                if "enum_id" in value_data:
                    result[field_id] = value_data["enum_id"]
                elif "value" in value_data:
                    result[field_id] = value_data["value"]
            else:
                enum_ids = [v.get("enum_id") for v in values if "enum_id" in v]
                if enum_ids:
                    result[field_id] = enum_ids
                else:
                    result[field_id] = [v.get("value") for v in values if "value" in v]

        return result

    def extract_lead_data(
        self, lead: dict[str, Any], contact: dict[str, Any]
    ) -> dict[str, Any]:  # pylint: disable=too-many-locals
        """
        Извлечь необходимые данные из сделки и контакта.

        Args:
            lead: Данные сделки из amoCRM
            contact: Данные контакта из amoCRM

        Returns:
            dict: Извлеченные данные
            {
                "lead_id": int,
                "price": int,
                "courses_count": int,
                "class_enum_id": int | None,
                "subjects_enum_ids": list[int],
                "direction_enum_id": int | None,
                "purchased_course_enum_ids": list[int],
                "contact_name": str,
                "contact_phone": str | None,
                "contact_email": str | None,
            }
        """
        logger.info("Extracting data from lead %s", lead.get("id"))

        lead_custom_fields = self._parse_custom_fields(lead.get("custom_fields_values", []))

        price = lead.get("price", 0)

        class_enum_id = lead_custom_fields.get(settings.AMO_LEAD_FIELD_CLASS)
        subjects_enum_ids = lead_custom_fields.get(settings.AMO_LEAD_FIELD_SUBJECTS, [])
        direction_enum_id = lead_custom_fields.get(settings.AMO_LEAD_FIELD_DIRECTION)
        purchased_course_enum_ids = lead_custom_fields.get(settings.AMO_LEAD_FIELD_PURCHASED_COURSE, [])

        if not isinstance(subjects_enum_ids, list):
            subjects_enum_ids = [subjects_enum_ids] if subjects_enum_ids else []

        if not isinstance(purchased_course_enum_ids, list):
            purchased_course_enum_ids = [purchased_course_enum_ids] if purchased_course_enum_ids else []

        contact_name = contact.get("name", "")

        contact_phone = None
        contact_email = None

        for field in contact.get("custom_fields_values", []):
            field_code = field.get("field_code")
            values = field.get("values", [])

            if field_code == "PHONE" and values:
                contact_phone = values[0].get("value")
            elif field_code == "EMAIL" and values:
                contact_email = values[0].get("value")

        logger.info(
            "Extracted lead data: price=%s, class=%s, subjects=%s, direction=%s",
            price,
            class_enum_id,
            subjects_enum_ids,
            direction_enum_id,
        )
        logger.info("Extracted contact data: name=%s, phone=%s, email=%s", contact_name, contact_phone, contact_email)

        return {
            "lead_id": lead.get("id"),
            "price": price,
            "class_enum_id": class_enum_id,
            "subjects_enum_ids": subjects_enum_ids,
            "direction_enum_id": direction_enum_id,
            "purchased_course_enum_ids": purchased_course_enum_ids,
            "contact_name": contact_name,
            "contact_phone": contact_phone,
            "contact_email": contact_email,
        }
